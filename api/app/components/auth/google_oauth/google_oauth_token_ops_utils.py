from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
import httpx

from app.logger.logging_setup import logger
from app.settings.env_settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_GRANT_TYPE, GOOGLE_OAUTH_REDIRECT_URI, GOOGLE_OAUTH_TOKEN_URL


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
    return await _post_token_request(token_data)


async def refresh_google_access_token(refresh_token: str) -> dict:
    token_data = {
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    logger.debug("Refreshing access token with refresh_token...")
    return await _post_token_request(token_data)


async def _post_token_request(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_OAUTH_TOKEN_URL, data=data)
        if response.status_code != 200:
            logger.error(f"Google API token error: {response.status_code} - {response.text}")
            response.raise_for_status()
        logger.debug("Token request successful.")
        return response.json()