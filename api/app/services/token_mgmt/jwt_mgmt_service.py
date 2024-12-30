from datetime import datetime, timedelta, timezone
import jwt

from app.services.config_mgmt_service import load_config

CONFIG = load_config()
AUTH = CONFIG.get("local_auth", {})
SECRET_KEY = AUTH.get("jwt_secret", "")
ALGORITHM = AUTH.get("algorithm", "")
JWT_EXPIRATION_TIME = AUTH.get("exp_time", "")


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