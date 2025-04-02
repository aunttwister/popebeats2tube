from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.services.jwt_mgmt_service import create_jwt
from app.settings.env_settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_REDIRECT_URI, GOOGLE_OAUTH_SCOPES

def construct_oauth_url() -> str:
    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_OAUTH_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_OAUTH_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={GOOGLE_OAUTH_SCOPES}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

def calculate_token_expiry(expires_in_seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)

def handle_token_exchange_errors(token_response: dict):
    if "error" in token_response:
        raise HTTPException(
            status_code=400,
            detail=token_response.get("error_description", "OAuth token exchange failed")
        )

def generate_jwt_response(user_id: str, returned_user_id: str = None) -> dict:
    jwt = create_jwt(user_id)
    return {
        "jwt": jwt["token"],
        "expires_in": jwt["expires_in"],
        "user_id": returned_user_id or user_id
    }
