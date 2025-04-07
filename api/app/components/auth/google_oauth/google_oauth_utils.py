from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
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

def is_token_expired(expiry: datetime) -> bool:
    return datetime.now(timezone.utc) >= expiry

def get_valid_refresh_token(token_response: dict, fallback_token: str) -> str:
    return token_response.get("refresh_token", fallback_token)
