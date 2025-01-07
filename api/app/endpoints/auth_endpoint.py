from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Session
from app.db.db import get_db_session
from app.dto import AuthRequestDto
from app.services.jwt_mgmt_service import create_jwt
from app.repositories.user_mgmt_repository import persist_credentials, verify_user_email
from app.services.google_oauth_service import get_google_oauth_credentials, verify_google_token, refresh_google_access_token
from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import logger
import httpx

# Load configuration
config = load_config()

auth_router = APIRouter()

@auth_router.post("/google")
async def google_auth(auth_request: AuthRequestDto):
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
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={config['google_oauth']['client_id']}"
            f"&redirect_uri=http://localhost:3000/auth/google/callback"
            f"&response_type=code"
            f"&scope={' '.join(config['google_oauth']['scopes'])}"
            f"&access_type=offline"
        )
        logger.debug(f"User needs to authenticate via Google OAuth.")
        logger.info(f"User {email} needs to authenticate via Google OAuth.")
        return {"redirect": True, "oauth_url": oauth_url, "user_id": user.id}

    # If credentials exist, proceed with normal login flow
    jwt_token = create_jwt(user_id=user.id)
    return {"redirect": False, "jwt": jwt_token["token"], "expires_in": jwt_token["expires_in"], "user_id": user.id}

@auth_router.post("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db_session)):
    """
    Handles the Google OAuth callback to exchange the authorization code for tokens.
    """
    # Log incoming request content
    request_body = await request.json()
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

        if "error" in token_response:
            logger.error(f"Token exchange error: {token_response['error_description']}")
            raise HTTPException(status_code=400, detail=token_response["error_description"])

        # Extract tokens and calculate expiry
        access_token = token_response["access_token"]
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response["expires_in"]

        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Persist credentials in the database
        user = persist_credentials(user_id, access_token, refresh_token, token_expiry, db)
        
        jwt = create_jwt(user_id)

        return {"jwt": jwt["token"], "expires_in": jwt["expires_in"],  "user_id": user.id}

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
    

@auth_router.post("/token-refresh")
async def refresh_auth_token(request: Request, db: Session = Depends(get_db_session)):
    """
    Refreshes the Google OAuth access token using the refresh token.
    """
    # Log incoming request content
    request_body = await request.json()
    user_email = request_body.get("user_email")
    logger.debug("Starting access token refresh process.")
    logger.info(f"Starting access token refresh process for user {user_email}.")
    
    user = verify_user_email(user_email)
    if not user or not user.youtube_refresh_token:
        logger.error("Invalid user or missing refresh token.")
        raise HTTPException(status_code=401, detail="Invalid user or missing refresh token.")

    try:
        token_response = await refresh_google_access_token(user.youtube_refresh_token)
        access_token = token_response["access_token"]
        
        refresh_token = token_response.get("refresh_token")
        if refresh_token is None:
            refresh_token = user.youtube_refresh_token
        
        new_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_response["expires_in"])
        logger.info(f"Google Api access token refresh successful. New expiry date is {new_expiry}.")
        
        # Update the user's token details in the database
        user = persist_credentials(user.id, access_token, refresh_token, new_expiry, db)

        # Generate new JWT
        new_jwt = create_jwt(user.id)

        return {"jwt": new_jwt["token"], "expires_in": new_jwt["expires_in"],  "user_id": user.id}
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")
