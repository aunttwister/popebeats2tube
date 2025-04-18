from dotenv import load_dotenv
import os

load_dotenv()

# Database
DB_CONN_STR = os.getenv("POPEBEATS2TUBE_DB_CONN_STR")

# File Share
FILE_SHARE_IP_ADDR = os.getenv("POPEBEATS2TUBE_FILE_SHARE_IP_ADDR")
FILE_SHARE_BASE_PATH = os.getenv("POPEBEATS2TUBE_FILE_SHARE_BASE_PATH")
FILE_SHARE_OS = os.getenv("POPEBEATS2TUBE_FILE_SHARE_OS")

# Google OAuth
GOOGLE_OAUTH_TOKEN_URL = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_TOKEN_URL")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_REDIRECT_URI")
GOOGLE_OAUTH_REDIRECT_URI_PATHS = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_REDIRECT_URI_PATHS")
GOOGLE_OAUTH_GRANT_TYPE = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_GRANT_TYPE")
GOOGLE_OAUTH_SCOPES = os.getenv("POPEBEATS2TUBE_GOOGLE_OAUTH_SCOPES")

# Local Auth
LOCAL_AUTH_ALGORITHM = os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_ALGORITHM")
LOCAL_AUTH_EXP_TIME = os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_EXP_TIME")
LOCAL_AUTH_JWT_SECRET = os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_JWT_SECRET")

# Admin
ADMIN_AUTH_TOKEN = os.getenv("POPEBEATS2TUBE_ADMIN_AUTH_TOKEN")

# Logging
LOGGING_LOG_DIR = os.getenv("POPEBEATS2TUBE_LOGGING_LOG_DIR")
LOGGING_LOG_FILE = os.getenv("POPEBEATS2TUBE_LOGGING_LOG_FILE")
LOGGING_ROTATION = os.getenv("POPEBEATS2TUBE_LOGGING_ROTATION")
LOGGING_RETENTION = os.getenv("POPEBEATS2TUBE_LOGGING_RETENTION")
LOGGING_COMPRESSION = os.getenv("POPEBEATS2TUBE_LOGGING_COMPRESSION")
LOGGING_ENABLE_ADVANCED_LOGGING = os.getenv("POPEBEATS2TUBE_LOGGING_ENABLE_ADVANCED_LOGGING")

# CORS Origins
CORS_ORIGINS = os.getenv("POPEBEATS2TUBE_CORS_ORIGINS")

# FFmpeg
FFMPEG_PATH = os.getenv("POPEBEATS2TUBE_FFMPEG_PATH")
FFMPEG_PROBE_PATH = os.getenv("POPEBEATS2TUBE_FFMPEG_PROBE_PATH")

# YouTube Access
YOUTUBE_ACCESS_SERVICE_NAME = os.getenv("POPEBEATS2TUBE_YOUTUBE_ACCESS_SERVICE_NAME")
YOUTUBE_ACCESS_SERVICE_VERSION = os.getenv("POPEBEATS2TUBE_YOUTUBE_ACCESS_SERVICE_VERSION")
YOUTUBE_ACCESS_CONCURRENCY_LIMIT = int(os.getenv("POPEBEATS2TUBE_YOUTUBE_ACCESS_CONCURRENCY_LIMIT", 3))

# Scheduler
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("POPEBEATS2TUBE_SCHEDULER_INTERVAL_MINUTES", 5))

# Switches
KILL_SWITCH_ENABLED = os.getenv("POPEBEATS2TUBE_KILL_SWITCH", "false").lower() == "true"
MAINTENANCE_MODE_ENABLED = os.getenv("POPEBEATS2TUBE_MAINTENANCE_MODE", "false").lower() == "true"

