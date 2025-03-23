from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests    
import httpx

from app.logger.logging_setup import logger

import os

# Load environment variables directly
GOOGLE_CLIENT_ID = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_SECRET", "")
TOKEN_URL = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_TOKEN_URL", "")
REDIRECT_URI = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_REDIRECT_URI", "")
GRANT_TYPE = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_GRANT_TYPE", "")


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
    logger.debug("Verifying Google OAuth2 token.")
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        logger.debug("Token verification successful.")
        logger.info(f"Token verified for user with email: {idinfo.get('email')}")
        return idinfo
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
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
    logger.debug("Preparing data for Google OAuth token exchange.")
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

    logger.debug("Initiating request to exchange authorization code for credentials.")
    try:
        # Use `httpx` for asynchronous HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            logger.debug("Token exchange request successful.")
            logger.info(f"Token exchange response: {response.json()}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token exchange: {e.response.text}")
        logger.info(f"Token data: {token_data}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error during token exchange: {e}")
        raise

async def refresh_google_access_token(refresh_token: str):
    """
    Refreshes the Google OAuth access token using the refresh token.

    Args:
    -----
    refresh_token : str
        The refresh token provided during the initial token exchange.

    Returns:
    --------
    dict
        A dictionary containing the new access token and related details.

    Raises:
    -------
    httpx.HTTPStatusError
        If the HTTP request to refresh the token fails.
    """
    token_url = TOKEN_URL
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    logger.debug("Initiating access token refresh...")
    logger.info(f"Initiating access token refresh with following request: {data}")
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            logger.error(f"Google API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        logger.debug("Access token refresh successful.")
        return response.json()
