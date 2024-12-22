"""
Logging configuration.

Sets up logging to a file with daily rotation and 7-day retention, using the Loguru library. Logs are also sent to the console at the INFO level.
"""
import sys
from loguru import logger
from settings.settings import LOG_DIR  # Import the global log path from settings

def setup_logging():
    """
    Sets up logging with the specified log directory.

    This function configures the logging system to log messages to both a file and the console. 
    The log file is rotated every day, and old logs are retained for 7 days in a compressed format.

    :return: A logger object configured with the specified settings.
    """
    logger.add(f"{LOG_DIR}/app.log", rotation="1 day", retention="7 days", compression="zip")
    logger.add(sys.stdout, level="INFO")  # Logs to console with INFO level

    return logger
