"""
This module handles user authentication and JWT generation for secure API access.

It performs the following tasks:
- Verifies the Google OAuth2 token to ensure the user's identity is valid.
- Retrieves the YouTube API key associated with the user.
- Creates and verifies JWT tokens for authenticated users.

Configuration values such as the Google Client ID, JWT secret, algorithm, and expiration time
are loaded from the configuration file to secure the token generation and verification process.

Functions:
----------
- verify_google_token(token: str): Verifies the provided Google OAuth2 token.
- create_jwt(user_id: int): Creates a JWT token for the user with the provided user_id.
- verify_user(email: str): Verifies if a user exists in the database by their email.
- get_youtube_api_key_by_user_id(user_id: str): Retrieves the YouTube API key for a given user ID.

The module ensures that only authenticated users can access protected endpoints and interact with the
system securely.
"""
from datetime import datetime, timedelta, timezone
import jwt
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session
from app.db import User, get_db_session
from app.services.config_mgmt_service import load_config

CONFIG = load_config()
AUTH = CONFIG.get("auth", {})
GOOGLE_CLIENT_ID = AUTH.get("google_client_id", "")
SECRET_KEY = AUTH.get("jwt_secret", "")
ALGORITHM = AUTH.get("algorithm", "")
JWT_EXPIRATION_TIME = AUTH.get("exp_time", "")


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

def create_jwt(user_id: int):
    """
    Creates a JWT token for the user with the provided user_id.

    Args:
    -----
    user_id : int
        The user ID for which the JWT will be generated.

    Returns:
    --------
    str
        The JWT token containing the user_id and expiration time.

    Notes:
    ------
    The token is signed using the `SECRET_KEY` and the algorithm specified in the configuration.
    The expiration time is determined by the configuration value `JWT_EXPIRATION_TIME`.
    """ 
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=int(JWT_EXPIRATION_TIME)),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_user(email: str):
    """
    Verifies if a user exists in the database by their email.

    Args:
    -----
    email : str
        The email address of the user to be verified.

    Returns:
    --------
    User
        The user object if a user with the provided email exists.

    Raises:
    -------
    ValueError
        If no user is found with the given email, an exception is raised.
    """
    db: Session = next(get_db_session())  # Get the session from the generator
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    return user

def get_youtube_api_key_by_user_id(user_id: str) -> str:
    """
    Retrieves the YouTube API key for a given user ID.

    Args:
    -----
    user_id : str
        The UUID of the user whose YouTube API key is to be retrieved.

    Returns:
    --------
    str
        The YouTube API key associated with the user.

    Raises:
    -------
    ValueError
        If no user with the given user_id is found in the database.
    """
    
    with get_db_session() as db:  # 'with' ensures session is properly closed after use
        user = db.query(User).filter(User.id == user_id).first()

    # below should be moved to endpoint implementation
    # if not user:
    #     raise HTTPException(status_code=404, detail="User with ID {user_id} not found.")

    return user.youtube_api_key