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
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import User, get_db_session
from app.dto import UserCreateDTO

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
    """
    db: Session = next(get_db_session())  # Get the session from the generator
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    return user

def persist_credentials(user_id: str, refresh_token: str, token_expiry: datetime, db: Session) -> str:
    """
    Updates the user's credentials in the database.

    Args:
    -----
    user_id : str
        The ID of the user whose credentials are to be updated.
    refresh_token : str
        The new refresh token.
    token_expiry : datetime
        The expiration time of the new access token.

    Returns:
    --------
    str
        The email of the user whose credentials were updated.

    Raises:
    -------
    ValueError
        If no user with the given user ID is found in the database.
    """
    try:
        # Retrieve user by ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found.")

        # Update credentials if missing
        if not user.refresh_token:
            user.refresh_token = refresh_token
        if not user.token_expiry:
            user.token_expiry = token_expiry

        db.commit()
        return user.email
    except Exception as e:
        db.rollback()  # Ensure rollback in case of failure
        raise Exception(f"Unable to persist user credentials. Message: {e}")
    
def create_user_in_db(user_dto: UserCreateDTO,
                      db: Session) -> dict:
    """
    Handles the business logic for creating a new user.

    Args:
    -----
    user_dto : UserCreateDTO
        The data transfer object containing the user details.
    db : Session
        The database session dependency.

    Returns:
    --------
    dict
        The created user details.

    Raises:
    -------
    HTTPException
        If a user with the same email already exists.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_dto.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create the new user
    new_user = User(
        email=user_dto.email,
        refresh_token=None,
        token_expiry=None,
        date_created=datetime.now(),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "date_created": new_user.date_created,
        "is_active": new_user.is_active
    }