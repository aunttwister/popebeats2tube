"""
Service Layer: File Transfer
============================
This module handles file transfers for uploaded files, moving them to configured shared paths.

Responsibilities:
-----------------
- Determine the type of file (audio or image).
- Transfer files to the appropriate shared location, including user-specific directories.
- Validate and create destination paths.

Logging:
--------
- DEBUG: Logs the start, intermediate steps, and success of operations.
- INFO: Includes sensitive details like file names and paths.
- ERROR: Logs failures during file transfer or path validation.

Functions:
----------
- transfer_file: Transfers a file to the configured shared location.
- get_file_type: Determines the type of the file based on its MIME type.
"""

import os
import shutil
from fastapi import UploadFile
from app.services.config_mgmt_service import load_config
from app.utils.file_path_util import generate_file_path, validate_and_create_path
import mimetypes
from app.logging.logging_setup import logger

# Load configuration
CONFIG = load_config()
FILE_SHARE_CONFIG = CONFIG.get("file_share", {})
IP_ADDR = FILE_SHARE_CONFIG.get("ip_addr", "")
BASE_PATH = FILE_SHARE_CONFIG.get("base_path", "")
AUDIO_PATH = FILE_SHARE_CONFIG.get("audio_path", "")
IMG_PATH = FILE_SHARE_CONFIG.get("img_path", "")


def transfer_file(file: UploadFile, user_email: str, video_title: str) -> str:
    """
    Transfer a file to the configured shared path.

    Args:
    -----
    file : UploadFile
        The uploaded file to transfer.
    user_email : str
        The email of the user (used to determine the storage directory).
    video_title : str
        The title of the video (used to create a unique directory for files).

    Returns:
    --------
    str
        The full destination path where the file was stored.

    Logs:
    -----
    - DEBUG: Start and success of file transfer.
    - INFO: Includes details of the file and destination.
    - ERROR: Logs failures during transfer or path validation.

    Raises:
    -------
    ValueError
        If the file_share configuration is invalid.
    """
    logger.debug(f"Starting file transfer for file: {file.filename}, user: {user_email}.")
    try:
        if not IP_ADDR or not BASE_PATH or not AUDIO_PATH or not IMG_PATH:
            logger.error("File share configuration is invalid.")
            raise ValueError("File share configuration is invalid. Please check 'ip_addr' and 'base_path'.")

        # Determine the file type
        file_type = get_file_type(file)
        logger.debug(f"File type determined: {file_type}.")

        # Generate the destination path
        destination_path = generate_file_path(IP_ADDR, BASE_PATH, user_email, video_title, file_type)
        logger.info(f"Generated destination path: {destination_path}.")

        # Ensure the destination directory exists
        validate_and_create_path(destination_path)

        # Define the destination file path
        destination_file = os.path.join(destination_path, file.filename)

        # Save the file to the destination
        with open(destination_file, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.debug(f"File transfer completed successfully for file: {file.filename}.")
        logger.info(f"File stored at: {destination_file}.")
        return destination_file
    except Exception as e:
        logger.error(f"Failed to transfer file {file.filename}: {str(e)}")
        raise Exception("Error occurred during file transfer.")


def get_file_type(file: UploadFile) -> str:
    """
    Determine the type of file ('audio' or 'image') based on its MIME type.

    Args:
    -----
    file : UploadFile
        The uploaded file to determine the type of.

    Returns:
    --------
    str
        The type of the file ('audio' or 'image').

    Logs:
    -----
    - DEBUG: File type determination.
    - ERROR: Unsupported file type or failure to determine file type.

    Raises:
    -------
    ValueError
        If the file type cannot be determined or is not supported.
    """
    logger.debug(f"Determining file type for file: {file.filename}.")
    try:
        # Extract MIME type using the file's filename or content type
        mime_type, _ = mimetypes.guess_type(file.filename)

        # Map MIME types to file types
        if mime_type and mime_type.startswith("audio/"):
            return "audio"
        elif mime_type and mime_type.startswith("image/"):
            return "image"
        else:
            logger.error(f"Unsupported file type: {file.filename}.")
            raise ValueError(f"Unsupported file type for file: {file.filename}")
    except Exception as e:
        logger.error(f"Failed to determine file type for file {file.filename}: {str(e)}")
        raise
