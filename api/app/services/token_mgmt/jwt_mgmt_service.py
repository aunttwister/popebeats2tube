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

from datetime import datetime, timedelta, timezone
import jwt
from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import log_message

# Load configuration values
CONFIG = load_config()
AUTH = CONFIG.get("local_auth", {})
SECRET_KEY = AUTH.get("jwt_secret", "")
ALGORITHM = AUTH.get("algorithm", "")
JWT_EXPIRATION_TIME = AUTH.get("exp_time", "")


def create_jwt(user_id: int) -> str:
    """
    Generates a JWT token for the specified user ID.

    Args:
    -----
    user_id : int
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

    Notes:
    ------
    - The token is signed using the `SECRET_KEY` and the algorithm specified in the configuration.
    - The expiration time is determined by the configuration value `JWT_EXPIRATION_TIME`.
    """
    log_message("DEBUG", f"Starting JWT creation for user ID: {user_id}")

    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=int(JWT_EXPIRATION_TIME)),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        log_message("DEBUG", f"JWT created for user ID: {user_id}")
        return token
    except Exception as e:
        log_message("ERROR", f"Failed to create JWT: {str(e)}")
        raise Exception("JWT creation failed. Please check the logs for details.")
