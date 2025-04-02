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
import os
import sys
from loguru import logger
from pathlib import Path
from app.settings.env_settings import LOGGING_LOG_DIR, LOGGING_LOG_FILE, LOGGING_ROTATION, LOGGING_RETENTION, LOGGING_COMPRESSION, LOGGING_ENABLE_ADVANCED_LOGGING

def setup_logging():
    """
    Sets up logging based on the global configuration loaded by config_loader.

    The function initializes logging parameters such as log file location, rotation,
    retention, compression, and log level using the settings defined as environment variables.

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

    log_dir = Path(LOGGING_LOG_DIR)
    log_file = LOGGING_LOG_FILE
    rotation = LOGGING_ROTATION
    retention = LOGGING_RETENTION
    compression = LOGGING_COMPRESSION
    enable_advanced_logging = LOGGING_ENABLE_ADVANCED_LOGGING.lower() == "true"

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

logger = setup_logging()