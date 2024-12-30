from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Session
from app.db import get_db_session
from app.dto import AuthRequestDto
from app.services.token_mgmt.jwt_mgmt_service import create_jwt
from app.repositories.user_mgmt_repository import persist_credentials, verify_user
from app.services.google_oauth_service import get_google_oauth_credentials, verify_google_token
from app.services.config_mgmt_service import load_config
import httpx

from app.utils.http_response_util import create_response

# Load configuration
config = load_config()

auth_router = APIRouter()

@auth_router.post("/google")
async def google_auth(auth_request: AuthRequestDto):
    """
    Handles Google OAuth login and checks for existing credentials.
    """
    try:
        idinfo = verify_google_token(auth_request.token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized access. Message: {e}.")

    email = idinfo.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid Google Token: Missing email.")

    user = verify_user(email)
    if not user:
        raise HTTPException(status_code=401, detail=f"User with email '{email}' is not authorized.")

    # If credentials are missing, provide an OAuth URL for the frontend to redirect
    if not user.refresh_token or not user.token_expiry:
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={config['google_oauth']['client_id']}"
            f"&redirect_uri=http://localhost:3000/auth/google/callback"
            f"&response_type=code"
            f"&scope={' '.join(config['google_oauth']['scopes'])}"
            f"&access_type=offline"
        )
        return {"redirect": True, "oauth_url": oauth_url, "user_id": user.id}

    # If credentials exist, proceed with normal login flow
    jwt_token = create_jwt(user_id=user.id)
    return {"redirect": False, "jwt": jwt_token}
    

@auth_router.post("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db_session)):
    """
    Handles the Google OAuth callback to exchange the authorization code for tokens.
    """
    try:
        # Parse JSON data from the incoming request
        data = await request.json()
        auth_code = data.get("code")
        user_id = data.get("user_id")
        error_message = data.get("error")

        if error_message:
            raise HTTPException(status_code=500, detail=error_message)

        # Exchange authorization code for tokens
        token_response = await get_google_oauth_credentials(auth_code)

        if "error" in token_response:
            raise HTTPException(status_code=400, detail=token_response["error_description"])

        # Extract tokens and calculate expiry
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response["expires_in"]
        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Persist credentials in the database
        email = persist_credentials(user_id, refresh_token, token_expiry, db)

        return create_response(200, "Successful operation.", f"Credentials persisted successfully for user {email}.")

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err.response.text}"
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
