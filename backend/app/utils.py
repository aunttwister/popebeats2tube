"""
File handling utilities.

This file contains a function to save uploaded files to the server. The function handles reading the file content and saving it to the specified directory.
"""

from fastapi import UploadFile
import os

async def save_file(file: UploadFile, upload_dir: str) -> str:
    """
    Saves an uploaded file to the specified directory.

    This function reads the content of the uploaded file and writes it to the specified directory on the server.

    :param file: The uploaded file object from FastAPI's UploadFile.
    :param upload_dir: The directory where the file will be saved.
    :return: The path where the file was saved.
    """
    # Ensure the upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create the file path where the file will be saved
    file_path = os.path.join(upload_dir, file.filename)
    
    # Open the file and write its content
    with open(file_path, "wb") as f:
        # Read the content of the uploaded file in chunks
        content = await file.read()
        f.write(content)

    return file_path
