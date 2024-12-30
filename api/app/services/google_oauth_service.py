from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests    
import httpx

from app.services.config_mgmt_service import load_config

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
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except ValueError as e:
        raise GoogleAuthError(f"Invalid or expired token: {e}")

async def get_google_oauth_credentials(auth_code):
    # Google OAuth token endpoint
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
        
        # Use `httpx` for asynchronous HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()