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
import mimetypes
import os
import shutil
import tempfile
from fastapi import UploadFile
from typing import List, Tuple
from app.db.db import Tune
from app.dto import TuneDto
from app.logger.logging_setup import logger
from app.settings.env_settings import FILE_SHARE_OS
from app.components.file_processing.file_processing_utils import base64_to_file, generate_file_path_non_windows, generate_file_path_windows, validate_and_create_path

def get_mp4_path(output_path: str, video_title: str) -> str:
    return os.path.join(output_path, f"{video_title}.mp4")

def get_audio_path(tune: Tune) -> str:
    return f"{tune.base_dest_path}/{tune.audio_name}"

def get_image_path(tune: Tune) -> str:
    return f"{tune.base_dest_path}/{tune.img_name}"

def persistence_preparation_processing(
    tune: TuneDto, user_id: str
) -> Tuple[str, str, Tuple[str, str], Tuple[str, str], str]:
    """
    Prepares files for DB persistence and later file move after DB success.

    Returns:
    - audio_final_path
    - img_final_path
    - audio_map: (temp_path, final_path)
    - img_map: (temp_path, final_path)
    - base_dest_path
    """
    img_file: UploadFile = base64_to_file(tune.img_file_base64, f"{tune.img_name}")
    audio_file: UploadFile = base64_to_file(tune.audio_file_base64, f"{tune.audio_name}")

    img_temp_path = save_temp_file(img_file)
    audio_temp_path = save_temp_file(audio_file)

    base_dest_path = generate_file_path(user_id, tune.video_title)

    img_final_path = os.path.join(base_dest_path, img_file.filename)
    audio_final_path = os.path.join(base_dest_path, audio_file.filename)

    return (
        (audio_temp_path, audio_final_path),
        (img_temp_path, img_final_path),
        base_dest_path
    )


def processing_commit(file_mappings: List[Tuple[str, str]]):
    for temp_path, final_path in file_mappings:
        move_temp_file(temp_path, final_path)

def save_temp_file(file: UploadFile) -> str:
    suffix = f".{file.filename.split('.')[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.file.seek(0)
        shutil.copyfileobj(file.file, tmp)
        logger.debug(f"Saved temp file for '{file.filename}' at '{tmp.name}'")
        return tmp.name


def move_temp_file(temp_path: str, final_path: str):
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    shutil.move(temp_path, final_path)
    logger.info(f"Moved temp file from '{temp_path}' to final destination '{final_path}'")


def cleanup_temp_files(temp_paths: List[str]):
    for path in temp_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up temp file: {path}")
            else:
                logger.warning(f"Temp file not found during cleanup: {path}")
        except Exception as e:
            logger.error(f"Failed to clean up temp file '{path}': {str(e)}")


def generate_file_path(user_id: str, video_title: str) -> str:
    """
    Generate a file path based on the operating system and user ID.

    Args:
    -----
    user_id : str
        The ID of the user (used to determine the storage directory).
    video_title : str
        The title of the video (used to create a unique directory for files).

    Returns:
    --------
    str
        The generated file path.

    Logs:
    -----
    - DEBUG: Generated file path.
    - ERROR: Logs failures during path generation.
    """
    logger.debug(f"Generating file path for user: {user_id}, video title: {video_title}.")
    try:
        if FILE_SHARE_OS.lower() == "windows":
            return generate_file_path_windows(user_id, video_title)
        else:
            return generate_file_path_non_windows(user_id, video_title)
    except Exception as e:
        logger.error(f"Failed to generate file path: {str(e)}")
        raise ValueError("Invalid file share configuration.")

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
        destination_path = generate_file_path(user_id, video_title)

        validate_and_create_path(destination_path)

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
