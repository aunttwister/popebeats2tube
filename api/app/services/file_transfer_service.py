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
from app.utils.file_util import generate_file_path_windows, validate_and_create_path
import mimetypes
from app.logging.logging_setup import logger


# Function to transfer multiple files
def transfer_files(files: list[UploadFile], user_id: str, video_title: str) -> str:
    """
    Transfer multiple files to the configured shared path.

    Args:
    -----
    files : list
        List of files as base64 strings to transfer.
    user_id : str
        The ID of the user (used to determine the storage directory).
    video_title : str
        The title of the video (used to create a unique directory for files).

    Returns:
    --------
    list
        A list of full destination paths where the files were stored.

    Logs:
    -----
    - DEBUG: Start and completion of file transfers.
    - INFO: Details of the files and destination.
    - ERROR: Logs failures during transfers or path validation.

    Raises:
    -------
    ValueError
        If the file_share configuration is invalid.
    """
    logger.debug(f"Starting file transfer for {len(files)} files, user: {user_id}.")
    try:
        # Generate the destination path
        destination_path = generate_file_path_windows(user_id, video_title)
        logger.info(f"Generated destination path: {destination_path}.")

        destination_path = validate_and_create_path(destination_path)

        for file in files:
            file_name = file.filename
            destination_file = os.path.join(destination_path, file_name)

            with open(destination_file, "wb") as f:
                shutil.copyfileobj(file.file, f)
                
            logger.debug(f"File {file_name} transferred successfully to {destination_file}.")

        logger.info(f"All {len(files)} files transferred successfully.")
        return destination_path
    except Exception as e:
        logger.error(f"Failed to transfer files: {str(e)}")
        raise Exception("Error occurred during file transfers.")


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
