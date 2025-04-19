from fastapi import HTTPException
import httpx
from requests import Session

from app.components.auth.google_oauth.google_oauth_static_utils import calculate_token_expiry, construct_oauth_url, get_valid_refresh_token
from app.components.auth.jwt_mgmt.jwt_mgmt_utils import generate_jwt_response
from app.components.user_mgmt.user_mgmt_repository import get_user_by_email, get_user_by_id
from app.components.user_mgmt.user_mgmt_service import update_user_credentials_service
from app.db.db import User
from .google_oauth_token_ops_utils import (
    refresh_google_access_token,
    verify_google_token
)
from app.logger.logging_setup import logger

def extract_and_verify_email(token: str) -> str:
    logger.debug("Verifying token and retrieving email...")
    try:
        idinfo = verify_google_token(token)
        email = idinfo.get("email")
        if not email:
            logger.error("Token verification succeeded, but no email found.")
            raise HTTPException(status_code=401, detail="Invalid Google Token: Missing email.")
        logger.debug(f"Email '{email}' extracted from token.")
        return email
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail=f"Unauthorized access. Message: {e}")


def get_and_validate_user_by_email(email: str, db: Session) -> User:
    logger.debug(f"Looking up user with email '{email}'...")
    user = get_user_by_email(email, db)
    if not user:
        logger.warning(f"User with email '{email}' not found in DB.")
        raise HTTPException(status_code=401, detail=f"User '{email}' is not authorized.")
    logger.debug(f"User '{email}' found and validated.")
    return user

def get_validated_user_by_id_for_refresh(user_id: str, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    if not user:
        logger.warning(f"Invalid user {user_id}")
        raise HTTPException(status_code=401, detail="Invalid user or missing refresh token.")
    return user


def should_redirect_for_oauth(user: User) -> bool:
    logger.debug("Checking for stored YouTube refresh token...")
    result = not user.youtube_refresh_token or not user.youtube_token_expiry
    if result:
        logger.info(f"User '{user.email}' requires Google OAuth authentication. Redirecting.")
    return result

def parse_and_store_token_response(token_response: dict, user_id: str, db: Session) -> User:
    logger.debug("Parsing token response for access and refresh tokens.")
    access_token = token_response["access_token"]
    refresh_token = get_valid_refresh_token(token_response, fallback_token=None)
    expiry = calculate_token_expiry(token_response["expires_in"])

    logger.debug(f"Storing tokens for user '{user_id}' with expiry {expiry}.")
    return update_user_credentials_service(user_id, access_token, refresh_token, expiry, db)

def build_oauth_redirect_response(user: User) -> dict:
    return {
        "redirect": True,
        "oauth_url": construct_oauth_url(user.email, user.id),
        "user_id": user.id,
    }

async def perform_token_refresh_and_update(user: User, db: Session):
    token_response = await refresh_google_access_token(user.youtube_refresh_token)
    access_token = token_response["access_token"]
    refresh_token = get_valid_refresh_token(token_response, user.youtube_refresh_token)
    expiry = calculate_token_expiry(token_response["expires_in"])

    logger.debug("Storing refreshed token values...")
    updated_user = update_user_credentials_service(user.id, access_token, refresh_token, expiry, db)
    logger.info(f"Token refresh successful for user {updated_user.id}")
    return generate_jwt_response(updated_user.id, updated_user.email)

def handle_token_refresh_http_error(e: httpx.HTTPStatusError, user: User):
    try:
        err_json = e.response.json()
        if err_json.get("error") == "invalid_grant":
            logger.warning("Refresh token invalid. Prompting user to reauthenticate.")
            return build_oauth_redirect_response(user)
    except Exception:
        logger.error("Failed to parse error response from Google.")

    logger.error(f"HTTP error during token refresh: {e.response.text}")
    raise HTTPException(status_code=e.response.status_code, detail=e.response.text)