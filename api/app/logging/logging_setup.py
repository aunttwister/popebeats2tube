"""
Module: logging_setup
======================
This module provides logging functionality for the application using the Loguru library.

Features:
---------
- Configurable logging parameters loaded from the global configuration (`config_loader`).
- Rotates between DEBUG, WARNING, ERROR, and CRITICAL levels by default.
- Enables INFO-level logging for web requests when `EnableAdvancedLogging` is set to true.
- Support for file-based logging with rotation, retention, and compression.
- A helper method for adding log messages programmatically.

Usage:
------
1. Call `setup_logging` during application startup to initialize the logging system.
2. Use `log_message` to log custom messages at runtime.

Dependencies:
-------------
- Requires `config_loader` to load global configuration from `config.json`.
- Requires the `loguru` library for advanced logging features.
"""
import sys
from loguru import logger
from pathlib import Path
from app.services.config_mgmt_service import load_config

def setup_logging():
    """
    Sets up logging based on the global configuration loaded by config_loader.

    The function initializes logging parameters such as log file location, rotation,
    retention, compression, and log level using the settings defined in `config.json`.

    Logging Modes:
    --------------
    - DEBUGLOG: Logs all messages of levels DEBUG, WARNING, ERROR, and CRITICAL.
    - INFO-level logging is enabled only if `EnableAdvancedLogging` is set to true.

    Log Message Format:
    -------------------
    All log messages follow the format:
        timestamp | LEVEL    | module:function:line - message

    :return: A logger object configured with the specified settings.
    """
    # Load global configuration
    config = load_config()

    # Retrieve logging configuration
    logging_config = config.get("logging", {})
    log_dir = Path(logging_config.get("log_dir", "./logs"))
    log_file = logging_config.get("log_file", "app.log")
    rotation = logging_config.get("rotation", "1 day")
    retention = logging_config.get("retention", "7 days")
    compression = logging_config.get("compression", "zip")
    enable_advanced_logging = logging_config.get("EnableAdvancedLogging", False)

    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define custom log format (same for console and file)
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Configure logger for file output (DEBUGLOG)
    logger.add(
        log_dir / log_file,
        rotation=rotation,
        retention=retention,
        compression=compression,
        format=log_format,
        level="DEBUG",
        filter=lambda record: record["level"].name in {"DEBUG", "WARNING", "ERROR", "CRITICAL"}
    )

    # Configure logger for INFO-level logging (conditionally enabled)
    if enable_advanced_logging:
        logger.add(
            log_dir / "info.log",
            rotation=rotation,
            retention=retention,
            compression=compression,
            format=log_format,
            level="INFO",
            filter=lambda record: record["level"].name == "INFO"
        )

    # Add console logging (DEBUGLOG and INFO-level logging)
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG",
        filter=lambda record: record["level"].name in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    )

    return logger


def log_message(level, message):
    """
    Logs a message at the specified log level.

    This function allows for dynamic logging of messages with different severity levels
    such as DEBUG, INFO, WARNING, ERROR, or CRITICAL.

    :param level: str
        The log level for the message (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    :param message: str
        The message to be logged.

    :raises ValueError:
        If the specified log level is invalid.
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}.")

    # Log the message at the specified level
    getattr(logger, level.lower())(message)
