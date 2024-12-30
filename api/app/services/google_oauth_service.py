from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests    
import httpx

from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import log_message

CONFIG = load_config()
GOOGLE_OAUTH = CONFIG.get("google_oauth", {})

GOOGLE_CLIENT_ID = GOOGLE_OAUTH.get("client_id", "")
GOOGLE_CLIENT_SECRET = GOOGLE_OAUTH.get("client_secret", "")
TOKEN_URL = GOOGLE_OAUTH.get("token_url", "")
REDIRECT_URI = GOOGLE_OAUTH.get("redirect_uri", "")
GRANT_TYPE = GOOGLE_OAUTH.get("grant_type", "")

def verify_google_token(token: str):
    """
    Verifies the provided Google OAuth2 token.

    Args:
    -----
    token : str
        The OAuth2 token obtained from the frontend via Google authentication.

    Returns:
    --------
    dict
        The decoded token data if the token is valid.

    Raises:
    -------
    GoogleAuthError
        If the token is invalid or expired, a Google authentication error is raised.
    """
    log_message("DEBUG", "Verifying Google OAuth2 token.")
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        log_message("DEBUG", "Token verification successful.")
        log_message("INFO", f"Token verified for user with email: {idinfo.get('email')}")
        return idinfo
    except ValueError as e:
        log_message("ERROR", f"Token verification failed: {e}")
        raise GoogleAuthError(f"Invalid or expired token: {e}")

async def get_google_oauth_credentials(auth_code: str):
    """
    Exchanges an authorization code for Google OAuth credentials.

    Args:
    -----
    auth_code : str
        The authorization code received from Google during the OAuth flow.

    Returns:
    --------
    dict
        A dictionary containing the access token and other related credentials.

    Raises:
    -------
    httpx.HTTPStatusError
        If the HTTP request to exchange the authorization code fails.
    """
    log_message("DEBUG", "Preparing data for Google OAuth token exchange.")
    token_url = TOKEN_URL
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    redirect_uri = REDIRECT_URI
    grant_type = GRANT_TYPE
    
    # Prepare data for token exchange
    token_data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": grant_type
    }

    log_message("DEBUG", "Initiating request to exchange authorization code for credentials.")
    try:
        # Use `httpx` for asynchronous HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            log_message("DEBUG", "Token exchange request successful.")
            log_message("INFO", f"Token exchange response: {response.json()}")
            return response.json()
    except httpx.HTTPStatusError as e:
        log_message("ERROR", f"HTTP error during token exchange: {e.response.text}")
        raise
    except Exception as e:
        log_message("CRITICAL", f"Unexpected error during token exchange: {e}")
        raise
