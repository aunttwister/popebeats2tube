import os
import shutil

from fastapi import UploadFile
from app.services.config_mgmt_service import load_config
from app.utils.file_path_util import generate_file_path, validate_and_create_path
import mimetypes

# Load configuration
CONFIG = load_config("base")
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

    Raises:
    -------
    ValueError
        If the file_share configuration is invalid.
    """
    if not IP_ADDR or not BASE_PATH or not AUDIO_PATH or not IMG_PATH:
        raise ValueError("File share configuration is invalid. Please check 'ip_addr' and 'base_path'.")

    # Determine the file type
    file_type = get_file_type(file)

    # Generate the destination path
    destination_path = generate_file_path(IP_ADDR, BASE_PATH, user_email, video_title, file_type)

    # Ensure the destination directory exists
    validate_and_create_path(destination_path)

    # Define the destination file path
    destination_file = os.path.join(destination_path, file.filename)

    # Save the file to the destination
    with open(destination_file, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return destination_file

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

    Raises:
    -------
    ValueError
        If the file type cannot be determined or is not supported.
    """
    # Extract MIME type using the file's filename or content type
    mime_type, _ = mimetypes.guess_type(file.filename)

    # Map MIME types to file types
    if mime_type and mime_type.startswith("audio/"):
        return "audio"
    elif mime_type and mime_type.startswith("image/"):
        return "image"
    else:
        raise ValueError(f"Unsupported file type for file: {file.filename}")
