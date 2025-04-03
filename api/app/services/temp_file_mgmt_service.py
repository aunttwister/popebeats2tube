import os
import shutil
import tempfile
from fastapi import UploadFile
from typing import List
from app.logger.logging_setup import logger

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
