from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests    
import httpx

from app.dto import AuthRequestDto
from app.logger.logging_setup import logger

from app.repositories.user_mgmt_repository import persist_credentials, verify_user_email, verify_user_id
from app.settings.env_settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_TOKEN_URL, GOOGLE_OAUTH_REDIRECT_URI, GOOGLE_OAUTH_GRANT_TYPE
from app.utils.auth_utils import construct_oauth_url, generate_jwt_response, handle_token_exchange_errors

async def handle_google_auth(auth_request: AuthRequestDto):
    """
    Handles Google OAuth login and checks for existing credentials.
    """
    # Log incoming request content
    logger.debug("Received Google OAuth login request.")
    logger.info(f"Received Google OAuth login request with content: {auth_request.model_dump_json()}")

    try:
        idinfo = verify_google_token(auth_request.token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized access. Message: {e}.")

    email = idinfo.get("email")
    if not email:
        logger.error("Google token is missing email.")
        raise HTTPException(status_code=401, detail="Invalid Google Token: Missing email.")

    user = verify_user_email(email)
    if not user:
        raise HTTPException(status_code=401, detail=f"User with email '{email}' is not authorized.")
    # If credentials are missing, provide an OAuth URL for the frontend to redirect
    if not user.youtube_refresh_token or not user.youtube_token_expiry:
        oauth_url = construct_oauth_url()
        logger.debug(f"User needs to authenticate via Google OAuth.")
        logger.info(f"User {email} needs to authenticate via Google OAuth.")
        return {"redirect": True, "oauth_url": oauth_url, "user_id": user.id}

    return generate_jwt_response(user.id)

async def handle_google_callback(request_body: dict, db):
    """
    Handles the Google OAuth callback to exchange the authorization code for tokens.
    """
    logger.debug("Received Google OAuth callback request.")
    logger.info(f"Received Google OAuth callback request with content: {request_body}")
    try:
        # Parse JSON data from the incoming request
        auth_code = request_body.get("code")
        user_id = request_body.get("user_id")
        error_message = request_body.get("error")

        if error_message:
            logger.error(f"Error during Google OAuth callback: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)

        # Exchange authorization code for tokens
        token_response = await get_google_oauth_credentials(auth_code)
        logger.debug("Successfully exchanged authorization code for tokens.")

        handle_token_exchange_errors(token_response)

        # Extract tokens and calculate expiry
        access_token = token_response["access_token"]
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response["expires_in"]

        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Persist credentials in the database
        user = persist_credentials(user_id, access_token, refresh_token, token_expiry, db)
        
        return generate_jwt_response(user.id)

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err.response.text}"
        )
    except ValueError as ve:
        logger.error(f"ValueError during Google OAuth callback: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.critical(f"Unhandled exception during Google OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

async def handle_token_refresh(user_id: str, db):
    """
    Refreshes the Google OAuth access token using the refresh token.
    """
    # Log incoming request content
    logger.debug("Starting access token refresh process.")
    logger.info(f"Starting access token refresh process for user {user_id}.")
    
    user = verify_user_id(user_id)
    if not user:
        logger.error("Invalid user.")
        raise HTTPException(status_code=401, detail="Invalid user.")
    if not user.youtube_refresh_token:
        logger.error("Missing refresh token.")
        raise HTTPException(status_code=401, detail="Missing refresh token.")
    try:
        if (datetime.now(timezone.utc) > user.youtube_token_expiry):
            token_response = await refresh_google_access_token(user.youtube_refresh_token)
            access_token = token_response["access_token"]
        
            refresh_token = token_response.get("refresh_token")
            if refresh_token is None:
                logger.warning("Google didn't provide a new refresh token. Continueing with the old one..")
                refresh_token = user.youtube_refresh_token
                new_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_response["expires_in"])
                logger.info(f"Google Api access token refresh successful. New expiry date is {new_expiry}.")
            # Update the user's token details in the database
            user = persist_credentials(user.id, access_token, refresh_token, new_expiry, db)

        return generate_jwt_response(user.id)
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")


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
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)
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
    token_url = GOOGLE_OAUTH_TOKEN_URL
    client_id = GOOGLE_OAUTH_CLIENT_ID
    client_secret = GOOGLE_OAUTH_CLIENT_SECRET
    redirect_uri = GOOGLE_OAUTH_REDIRECT_URI
    grant_type = GOOGLE_OAUTH_GRANT_TYPE
    
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
    token_url = GOOGLE_OAUTH_TOKEN_URL
    client_id = GOOGLE_OAUTH_CLIENT_ID
    client_secret = GOOGLE_OAUTH_CLIENT_SECRET

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
