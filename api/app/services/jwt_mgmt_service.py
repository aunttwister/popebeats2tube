"""
Module: token_mgmt_service
===========================
This module provides functionality for managing JSON Web Tokens (JWTs) to secure API access.

Responsibilities:
-----------------
- Creating JWT tokens for authenticated users.
- Configuring JWT signing parameters (secret, algorithm, and expiration time) from the global configuration.

Logging:
--------
This module includes detailed logging to assist with debugging and monitoring:
- DEBUG-level logs provide non-sensitive operational information.
- INFO-level logs include sensitive information (e.g., user IDs) and are logged only when advanced logging is enabled.

Configuration:
--------------
Values such as the JWT secret, algorithm, and expiration time are loaded from the configuration file.

Functions:
----------
- create_jwt(user_id: int): Generates a JWT token for the specified user ID.
"""

from datetime import datetime, timedelta
from uuid import UUID
import jwt
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from app.logger.logging_setup import logger
from app.settings.env_settings import LOCAL_AUTH_JWT_SECRET, LOCAL_AUTH_ALGORITHM, LOCAL_AUTH_EXP_TIME


def create_jwt(user_id: UUID) -> str:
    """
    Generates a JWT token for the specified user ID.

    Args:
    -----
    user_id : UUID
        The user ID for which the JWT will be generated.

    Returns:
    --------
    str
        A signed JWT token containing the user ID and expiration time.

    Logs:
    -----
    - DEBUG: Indicate the start and end of token creation.
    - INFO: Include the user ID for which the token is created (if advanced logging is enabled).
    - ERROR: Exclude sensitive information and describe the nature of the failure.

    Raises:
    -------
    Exception
        If token creation fails due to configuration issues or unexpected errors.
    """
    logger.debug(f"Starting JWT creation for user ID: {user_id}")

    try:
        expiration = datetime.now() + timedelta(seconds=int(LOCAL_AUTH_EXP_TIME))
        payload = {
            "user_id": str(user_id),
            "exp": expiration,
        }
        token = jwt.encode(payload, LOCAL_AUTH_JWT_SECRET, algorithm=LOCAL_AUTH_ALGORITHM)
        logger.debug(f"JWT created for user ID: {user_id}")
        return {"token": token, "expires_in": LOCAL_AUTH_EXP_TIME}
    except Exception as e:
        logger.error(f"Failed to create JWT: {str(e)}")
        raise Exception("JWT creation failed. Please check the logs for details.")


def extract_user_id_from_token(token: str) -> UUID:
    """
    Extract user_id from the JWT token.

    Args:
    -----
    token : str
        The JWT token containing user claims.

    Returns:
    --------
    UUID
        The user ID extracted from the token.

    Raises:
    -------
    HTTPException
        401: If the token is invalid or the user_id is not found.
    """
    logger.debug(f"Starting  current user extraction from token.")
    logger.info(f"Starting  current user extraction from token: {token}")
    try:
        logger.debug(f"Decoding JWT...")
        payload = jwt.decode(token, LOCAL_AUTH_JWT_SECRET, algorithms=[LOCAL_AUTH_ALGORITHM])
        logger.info(f"Decoded JWT: {payload}")
        logger.debug(f"Extracting user_id...")
        user_id = payload.get("user_id")
        logger.info(f"Extracted user_id: {user_id}")
        logger.debug(f"User_id extraction successful.")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return UUID(user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

