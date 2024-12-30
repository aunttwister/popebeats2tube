"""
Module: user_mgmt_repository
=============================
This module provides functions for managing user authentication and credentials in the database.

Responsibilities:
-----------------
- Verifying the existence of users by their email addresses.
- Persisting or updating user credentials such as refresh tokens and token expiry.
- Creating new users in the database.

Logging:
--------
This module includes detailed logging to assist with debugging and operational monitoring:
- DEBUG-level logs provide general operational flow information.
- INFO-level logs include details about sensitive operations (e.g., email addresses) when advanced logging is enabled.

Functions:
----------
- verify_user(email: str): Check if a user exists in the database by their email.
- persist_credentials(user_id: str, refresh_token: str, token_expiry: datetime, db: Session): Update user credentials in the database.
- create_user_in_db(user_dto: UserCreateDTO, db: Session): Add a new user to the database.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.db import User, get_db_session
from app.dto import UserCreateDTO
from app.logging.logging_setup import log_message


def verify_user(email: str):
    """
    Check if a user exists in the database by their email.

    Args:
    -----
    email : str
        The email address of the user to verify.

    Returns:
    --------
    User or None
        The user object if a matching email is found; otherwise, None.

    Logs:
    -----
    - DEBUG: Indicate the start and end of the verification process.
    - INFO: Include the email being verified (if advanced logging is enabled).
    """
    log_message("DEBUG", "Starting user verification.")
    log_message("INFO", f"Verifying user with email: {email}")

    db: Session = next(get_db_session())
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            log_message("DEBUG", "User verification successful.")
            log_message("INFO", f"User found: {email}")
        else:
            log_message("WARNING", "User verification failed. User not found.")
    finally:
        db.close()

    return user


def persist_credentials(user_id: str, refresh_token: str, token_expiry: datetime, db: Session) -> str:
    """
    Update the user's credentials in the database.

    Args:
    -----
    user_id : str
        The ID of the user whose credentials are being updated.
    refresh_token : str
        The new refresh token.
    token_expiry : datetime
        The expiration time of the new access token.
    db : Session
        The database session.

    Returns:
    --------
    str
        The email of the user whose credentials were updated.

    Raises:
    -------
    ValueError
        If no user with the specified user ID is found.

    Logs:
    -----
    - DEBUG: Indicate the start and end of credential persistence.
    - INFO: Include the user ID and email (if advanced logging is enabled).
    - ERROR: Exclude sensitive information (e.g., email or tokens).
    """
    log_message("DEBUG", f"Persisting credentials for user ID: {user_id}.")
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            log_message("ERROR", "User not found for credential persistence.")
            raise ValueError(f"User with ID {user_id} not found.")

        # Update credentials if missing
        if not user.refresh_token:
            user.refresh_token = refresh_token
        if not user.token_expiry:
            user.token_expiry = token_expiry

        db.commit()
        log_message("DEBUG", f"Credentials persisted successfully for user ID: {user_id}.")
        log_message("INFO", f"Credentials persisted for user email: {user.email}")
        return user.email
    except Exception as e:
        db.rollback()
        log_message("ERROR", f"Failed to persist credentials for user ID {user_id}: {str(e)}")
        raise Exception("Unable to persist user credentials. Please check the logs for more details.")


def create_user_in_db(user_dto: UserCreateDTO, db: Session) -> dict:
    """
    Create a new user in the database.

    Args:
    -----
    user_dto : UserCreateDTO
        The data transfer object containing the user details.
    db : Session
        The database session dependency.

    Returns:
    --------
    dict
        A dictionary containing the created user's details.

    Raises:
    -------
    ValueError
        If a user with the same email already exists.

    Logs:
    -----
    - DEBUG: Indicate the start and end of user creation.
    - INFO: Include the email of the created user (if advanced logging is enabled).
    - ERROR: Exclude sensitive information (e.g., email).
    """
    log_message("DEBUG", "Starting user creation process.")
    log_message("INFO", f"Creating user with email: {user_dto.email}")

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_dto.email).first()
        if existing_user:
            log_message("ERROR", "User creation failed: Email already exists.")
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

        log_message("DEBUG", f"User created successfully with ID: {new_user.id}.")
        log_message("INFO", f"User created: {user_dto.email}")
        return {
            "id": new_user.id,
            "email": new_user.email,
            "date_created": new_user.date_created,
            "is_active": new_user.is_active
        }
    except Exception as e:
        db.rollback()
        log_message("ERROR", f"Failed to create user: {str(e)}")
        raise Exception("Unable to create user. Please check the logs for more details.")
