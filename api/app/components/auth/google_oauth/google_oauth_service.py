from fastapi import HTTPException
import httpx
from requests import Session

from app.components.auth.google_oauth.google_oauth_service_validation import build_oauth_redirect_response, extract_and_verify_email, get_and_validate_user_by_email, get_validated_user_by_id_for_refresh, handle_token_refresh_http_error, parse_and_store_token_response, perform_token_refresh_and_update, should_redirect_for_oauth
from app.db.db import User
from app.dto import AuthRequestDto
from app.logger.logging_setup import logger
from app.components.user_mgmt.user_mgmt_service import (
    update_user_credentials_service,
    get_user_by_id,
)
from app.components.auth.jwt_mgmt.jwt_mgmt_utils import generate_jwt_response
from app.components.auth.google_oauth.google_oauth_static_utils import (
    construct_oauth_url,
    get_valid_refresh_token,
    is_token_expired,
    handle_token_exchange_errors,
    calculate_token_expiry,
)
from .google_oauth_token_ops_utils import (
    get_google_oauth_credentials,
    refresh_google_access_token,
)


async def handle_google_auth(auth_request: AuthRequestDto, db: Session):
    logger.debug("handle_google_auth method called")
    logger.info(f"OAuth login request received: {auth_request.model_dump_json()}")

    email = extract_and_verify_email(auth_request.token)
    user = get_and_validate_user_by_email(email, db)

    if should_redirect_for_oauth(user):
        return {
            "redirect": True,
            "oauth_url": construct_oauth_url(user.email, user.id),
            "user_id": user.id,
        }

    logger.info(f"User '{email}' is authorized. Generating JWT.")
    return generate_jwt_response(user.id, user.email)


async def handle_google_callback(request_body: dict, db: Session):
    logger.debug("handle_google_callback method called")
    logger.info(f"OAuth callback received: {request_body}")

    if request_body.get("error"):
        logger.error(f"OAuth callback error: {request_body['error']}")
        raise HTTPException(status_code=500, detail=request_body["error"])

    try:
        logger.debug("Exchanging auth code for access/refresh tokens...")
        token_response = await get_google_oauth_credentials(request_body["code"])

        handle_token_exchange_errors(token_response)
        logger.info(f"Token is valid. Token content: {token_response}")

        logger.debug(f"Tokens retrieved successfully. Storing for user {request_body['user_id']}...")
        user = parse_and_store_token_response(token_response, request_body["user_id"], db)

        logger.info(f"Credentials updated. Returning JWT for user {user.id}")
        return generate_jwt_response(user.id, user.email)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during callback: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.critical(f"Unexpected error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

async def handle_token_refresh(user_id: str, db: Session):
    logger.debug("handle_token_refresh method called")
    logger.info(f"Starting token refresh for user {user_id}")

    user = get_validated_user_by_id_for_refresh(user_id, db)

    if should_redirect_for_oauth(user):
        logger.warning("Refresh token is missing. Prompting user to reauthenticate.")
        return build_oauth_redirect_response(user)

    if not is_token_expired(user.youtube_token_expiry):
        logger.debug("Access token is still valid. No refresh needed.")
        return generate_jwt_response(user.id, user.email)

    try:
        logger.debug("Access token expired. Refreshing...")
        return await perform_token_refresh_and_update(user, db)

    except httpx.HTTPStatusError as e:
        return handle_token_refresh_http_error(e, user)

    except Exception as e:
        logger.critical(f"Unhandled exception during token refresh: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

# will be obsoleted upon schedule tune handling refactor
async def validate_and_refresh_token(user: User, db: Session):
    logger.debug("validate_and_refresh_token method called")
    logger.debug(f"Validating token expiry for user {user.id}")

    if not is_token_expired(user.youtube_token_expiry):
        logger.debug("Access token still valid. No action required.")
        return

    try:
        logger.debug("Token expired. Refreshing...")
        token_response = await refresh_google_access_token(user.youtube_refresh_token)
        access_token = token_response["access_token"]
        refresh_token = get_valid_refresh_token(token_response, user.youtube_refresh_token)
        expiry = calculate_token_expiry(token_response["expires_in"])

        update_user_credentials_service(user.id, access_token, refresh_token, expiry, db)
        logger.info(f"Token refreshed and saved for user {user.id}")
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")