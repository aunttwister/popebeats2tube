import os
from datetime import datetime
from typing import Literal

def generate_file_path(
    ip_addr: str,
    base_path: str,
    user_email: str,
    video_title: str,
    file_type: Literal["audio", "image"],
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
    if file_type not in {"audio", "image"}:
        raise ValueError("Invalid file type. Must be 'audio' or 'image'.")

    # Replace '@' in the email with '_'
    sanitized_email = user_email.replace("@", "_")

    # Build the file path
    file_path = os.path.join(
        f"\\\\{ip_addr}",
        base_path.replace("/", "\\"),
        sanitized_email,
        video_title.replace("/", "_"),
        file_type,
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
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
