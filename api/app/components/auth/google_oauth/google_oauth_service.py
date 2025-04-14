from fastapi import HTTPException
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests    
import httpx
from requests import Session

from app.db.db import User
from app.dto import AuthRequestDto
from app.logger.logging_setup import logger

from app.components.user_mgmt.user_mgmt_service import update_user_credentials_service, get_user_by_email, get_user_by_id
from app.components.auth.google_oauth.google_oauth_utils import calculate_token_expiry, construct_oauth_url, get_valid_refresh_token, handle_token_exchange_errors, is_token_expired
from app.components.auth.jwt_mgmt.jwt_mgmt_utils import generate_jwt_response
from app.settings.env_settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_TOKEN_URL, GOOGLE_OAUTH_REDIRECT_URI, GOOGLE_OAUTH_GRANT_TYPE

# -------------------------------------------------------------------------
# Public Methods
# -------------------------------------------------------------------------

async def handle_google_auth(auth_request: AuthRequestDto, db: Session):
    logger.debug("Received Google OAuth login request.")
    logger.info(f"Received Google OAuth login request with content: {auth_request.model_dump_json()}")

    try:
        idinfo = verify_google_token(auth_request.token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized access. Message: {e}")

    email = idinfo.get("email")
    if not email:
        logger.error("Google token is missing email.")
        raise HTTPException(status_code=401, detail="Invalid Google Token: Missing email.")

    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=401, detail=f"User with email '{email}' is not authorized.")

    if not user.youtube_refresh_token or not user.youtube_token_expiry:
        logger.debug(f"User {email} needs to authenticate via Google OAuth.")
        oauth_url = construct_oauth_url()
        return {"redirect": True, "oauth_url": oauth_url, "user_id": user.id}

    return generate_jwt_response(user.id)


async def handle_google_callback(request_body: dict, db: Session):
    logger.debug("Received Google OAuth callback request.")
    logger.info(f"Received Google OAuth callback request with content: {request_body}")

    try:
        if request_body.get("error"):
            logger.error(f"OAuth callback error: {request_body['error']}")
            raise HTTPException(status_code=500, detail=request_body["error"])

        token_response = await get_google_oauth_credentials(request_body["code"])
        handle_token_exchange_errors(token_response)

        access_token = token_response["access_token"]
        refresh_token = get_valid_refresh_token(token_response, fallback_token=None)
        expiry = calculate_token_expiry(token_response["expires_in"])
        
        user_id = request_body["user_id"]
        user = update_user_credentials_service(user_id, access_token, refresh_token, expiry, db)
        return generate_jwt_response(user.id)

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err.response.text}",
        )
    except ValueError as ve:
        logger.error(f"ValueError during Google OAuth callback: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.critical(f"Unhandled exception during Google OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


async def handle_token_refresh(user_id: str, db: Session):
    logger.debug("Starting access token refresh process.")
    logger.info(f"Refreshing token for user {user_id}")

    user = get_user_by_id(user_id, db)
    if not user or not user.youtube_refresh_token:
        raise HTTPException(status_code=401, detail="Invalid user or missing refresh token.")

    if not is_token_expired(user.youtube_token_expiry):
        return generate_jwt_response(user.id)

    try:
        token_response = await refresh_google_access_token(user.youtube_refresh_token)
        access_token = token_response["access_token"]
        refresh_token = get_valid_refresh_token(token_response, user.youtube_refresh_token)
        expiry = calculate_token_expiry(token_response["expires_in"])

        user = update_user_credentials_service(user.id, access_token, refresh_token, expiry, db)
        return generate_jwt_response(user.id)

    except httpx.HTTPStatusError as http_err:
        # Decode and handle Google's error response
        try:
            error_data = http_err.response.json()
            if error_data.get("error") == "invalid_grant":
                logger.warning("Refresh token expired or revoked. Re-authentication required.")
                oauth_url = construct_oauth_url()
                return {
                    "redirect": True,
                    "oauth_url": oauth_url,
                    "user_id": user.id
                }
        except Exception:
            pass  # fallback to generic error

        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Token refresh failed: {http_err.response.text}"
        )

    except Exception as e:
        logger.error(f"Unhandled error during token refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")


async def validate_and_refresh_token(user: User, db: Session):
    logger.debug("Starting token validation for user.")
    if not is_token_expired(user.youtube_token_expiry):
        return

    logger.debug("Access token expired. Refreshing...")
    try:
        token_response = await refresh_google_access_token(user.youtube_refresh_token)
        access_token = token_response["access_token"]
        refresh_token = get_valid_refresh_token(token_response, user.youtube_refresh_token)
        expiry = calculate_token_expiry(token_response["expires_in"])

        update_user_credentials_service(user.id, access_token, refresh_token, expiry, db)
        logger.info("Token refreshed and persisted.")
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")


# -------------------------------------------------------------------------
# Supporting Methods
# -------------------------------------------------------------------------

def verify_google_token(token: str) -> dict:
    logger.debug("Verifying Google OAuth2 token.")
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)
        logger.info(f"Token verified for user: {idinfo.get('email')}")
        return idinfo
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise GoogleAuthError(f"Invalid or expired token: {e}")


async def get_google_oauth_credentials(auth_code: str) -> dict:
    token_data = {
        "code": auth_code,
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
        "grant_type": GOOGLE_OAUTH_GRANT_TYPE,
    }
    logger.debug("Exchanging auth code for tokens...")
    return await post_token_request(token_data)


async def refresh_google_access_token(refresh_token: str) -> dict:
    token_data = {
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    logger.debug("Refreshing access token with refresh_token...")
    return await post_token_request(token_data)


async def post_token_request(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_OAUTH_TOKEN_URL, data=data)
        if response.status_code != 200:
            logger.error(f"Google API token error: {response.status_code} - {response.text}")
            response.raise_for_status()
        logger.debug("Token request successful.")
        return response.json()