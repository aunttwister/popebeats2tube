"""
Module: load_config
-------------------
This module provides a function to load application configuration settings from environment 
variables using the `dotenv` package. The function ensures configuration values are only 
loaded once per execution to optimize performance.

Key Features:
- Loads environment variables from a `.env` file if present.
- Provides a structured configuration dictionary.
- Avoids global variables for security and thread safety.
- Ensures sensitive data (e.g., secrets, tokens) is managed securely.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def get_env_list(env_var: str) -> list:
    """
    Retrieves a list from a comma-separated environment variable.

    Parameters
    ----------
    env_var : str
        The name of the environment variable.

    Returns
    -------
    list
        A list of strings derived from the environment variable.
    """
    return os.getenv(env_var, "").split(",")


def load_config() -> dict:
    """
    Loads application configuration settings from environment variables.

    This function retrieves all configuration settings from the system environment or a `.env` file.
    It structures the configuration into a dictionary to provide easy access to application settings.

    Returns
    -------
    dict
        A dictionary containing the parsed configuration settings.

    Example
    -------
    >>> config = load_config()
    >>> print(config["db"]["conn_str"])
    'mysql+mysqlconnector://devppav:o5AJckx!^tTy^mR@192.168.1.100/popebeats2tube.dev'
    """
    config = {
        "db": {
            "conn_str": os.getenv("POPEBEATS2TUBE_DB_CONN_STR")
        },
        "file_share": {
            "ip_addr": os.getenv("POPEBEATS2TUBE_FILE_SHARE_IP_ADDR"),
            "base_path": os.getenv("POPEBEATS2TUBE_FILE_SHARE_BASE_PATH")
        },
        "google_oauth": {
            "token_url": os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_TOKEN_URL"),
            "client_id": os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_ID"),
            "client_secret": os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_SECRET"),
            "redirect_uri": os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_REDIRECT_URI"),
            "grant_type": os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_GRANT_TYPE"),
            "scopes": get_env_list("POPEBEATS2TUBE_GOOGLE_OAUTH_SCOPES")
        },
        "local_auth": {
            "algorithm": os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_ALGORITHM"),
            "exp_time": os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_EXP_TIME"),
            "jwt_secret": os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_JWT_SECRET")
        },
        "admin": {
            "auth_token": os.getenv("POPEBEATS2TUBE_ADMIN_AUTH_TOKEN")
        },
        "logging": {
            "log_dir": os.getenv("POPEBEATS2TUBE_LOGGING_LOG_DIR"),
            "log_file": os.getenv("POPEBEATS2TUBE_LOGGING_LOG_FILE"),
            "rotation": os.getenv("POPEBEATS2TUBE_LOGGING_ROTATION"),
            "retention": os.getenv("POPEBEATS2TUBE_LOGGING_RETENTION"),
            "compression": os.getenv("POPEBEATS2TUBE_LOGGING_COMPRESSION"),
            "EnableAdvancedLogging": os.getenv("POPEBEATS2TUBE_LOGGING_ENABLE_ADVANCED_LOGGING") == "true"
        },
        "ffmpeg": {
            "path": os.getenv("POPEBEATS2TUBE_FFMPEG_PATH"),
            "probe_path": os.getenv("POPEBEATS2TUBE_FFMPEG_PROBE_PATH")
        },
        "youtube_access": {
            "service_name": os.getenv("POPEBEATS2TUBE_YOUTUBE_ACCESS_SERVICE_NAME"),
            "service_version": os.getenv("POPEBEATS2TUBE_YOUTUBE_ACCESS_SERVICE_VERSION")
        }
    }
    
    return config
