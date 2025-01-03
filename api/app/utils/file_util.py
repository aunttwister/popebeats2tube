import base64
import io
import os
from app.logging.logging_setup import logger

from fastapi import UploadFile

def generate_file_path(
    ip_addr: str,
    base_path: str,
    user_id: str,
    video_title: str
) -> str:
    """
    Generate a structured file path for audio or image files based on parameters.

    Args:
    -----
    ip_addr : str
        The IP address of the file server.
    base_path : str
        The base directory path for file storage.
    user_email : str
        The email address of the user (used to determine the user-specific directory).
    video_title : str
        The title of the video (used to create a unique directory for the files).
    file_type : Literal["audio", "image"]
        The type of file ("audio" or "image"), used to determine the subdirectory.

    Returns:
    --------
    str
        The generated file path.

    Raises:
    -------
    ValueError
        If `file_type` is not "audio" or "image".
    """
    sanitized_base_path = base_path.replace(':', '$').replace("/", "\\")
    sanitized_id = user_id.replace("-", "_")
    sanitized_video_title = video_title.replace("/", "_")
    logger.debug(f"Parameters for file path generation: ip_addr={ip_addr}, base_path={sanitized_base_path}, user_id={sanitized_id}, video_title={sanitized_video_title}")
    # Build the file path
    file_path = os.path.join(
        f"\\\\{ip_addr}",
        sanitized_base_path,
        sanitized_id,
        sanitized_video_title
    )

    return file_path


def validate_and_create_path(path: str) -> None:
    """
    Validate the file path and create directories if they do not exist.

    Args:
    -----
    path : str
        The file path to validate and prepare.

    Raises:
    -------
    OSError
        If the path is invalid or cannot be created.
    """
    print(path)
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    
def base64_to_file(base64_string: str, filename: str) -> UploadFile:
    """
    Converts a base64 string to an UploadFile-like object.

    Args:
    -----
    base64_string : str
        The base64-encoded string.
    filename : str
        The desired filename for the file.

    Returns:
    --------
    UploadFile
        An in-memory UploadFile-like object.

    Raises:
    -------
    ValueError: If the base64 string is invalid or cannot be decoded.
    """
    try:
        file_data = base64.b64decode(base64_string)
        file_obj = io.BytesIO(file_data)
        file_obj.name = filename
        return UploadFile(filename=filename, file=file_obj)
    except Exception as e:
        raise ValueError(f"Failed to convert base64 to file: {e}")
