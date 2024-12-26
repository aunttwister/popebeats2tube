# """
# This module provides API endpoints for uploading image and audio files.

# It uses FastAPI for creating the API and Loguru for logging. The module supports the following endpoints:
# - POST /upload/ : Allows uploading a single image and audio file.
# - POST /batch_upload/ : Allows uploading multiple image and audio files at once.

# The module validates the file type based on predefined allowed extensions and logs relevant information.
# """
# from fastapi import APIRouter, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
# from app.config import setup_logging
# #from ..utils import save_file
# from ..settings import AUDIO_DIR, IMAGE_DIR  # Import global paths for audio and image

# # Initialize the logger once
# logger = setup_logging()

# app = APIRouter()

# ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac'}
# ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# def allowed_file(filename, allowed_extensions):
#     """Check if the file is allowed based on its extension."""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# @app.post("/upload")
# async def upload_file(audiofile: UploadFile = File(...), imagefile: UploadFile = File(...)):
#     """Single file upload endpoint for audio or picture."""
#     logger.info("Started file upload.")

#     if not allowed_file(audiofile.filename, ALLOWED_AUDIO_EXTENSIONS):
#         logger.error(f"Invalid audio file type: {audiofile.filename}. Allowed audio types are {ALLOWED_AUDIO_EXTENSIONS}.")
#         raise HTTPException(status_code=400, detail="Invalid file type")
    
#     if not allowed_file(imagefile.filename, ALLOWED_IMAGE_EXTENSIONS):
#         logger.error(f"Invalid image file type: {imagefile.filename}. Allowed image types are {ALLOWED_IMAGE_EXTENSIONS}")
#         raise HTTPException(status_code=400, detail="Invalid file type")
#     # Check the file type and save it accordingly

#     audio_file_path = await save_file(audiofile, AUDIO_DIR)
#     logger.info(f"Audio file uploaded successfully: {audio_file_path}")
    
#     image_file_path = await save_file(imagefile, IMAGE_DIR)
#     logger.info(f"Image file uploaded successfully: {image_file_path}")
    
#     logger.info("Files uploaded successfully.")
#     return JSONResponse(content={"message": "Files uploaded successfully", "audio_file_path": audio_file_path, "image_file_path": image_file_path}, status_code=200)

# @app.post("/batch_upload")
# async def batch_upload(audio_files: list[UploadFile] = File(...), image_files: list[UploadFile] = File(...)):
#     """Batch upload endpoint for audio and picture files."""
#     logger.info("Started batch upload.")

#     uploaded_files = {'audio_files': [], 'image_files': []}

#     for audio_file in audio_files:
#         if allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
#             audio_path = await save_file(audio_file, AUDIO_DIR)
#             uploaded_files['audio_files'].append(audio_path)
#             logger.info(f"Uploaded audio file: {audio_path}")
#         else:
#             logger.error(f"Invalid audio file: {audio_file.filename}")
#             raise HTTPException(status_code=400, detail=f"Invalid audio file: {audio_file.filename}")
    
#     for image_file in image_files:
#         if allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
#             image_path = await save_file(image_file, IMAGE_DIR)
#             uploaded_files['image_files'].append(image_path)
#             logger.info(f"Uploaded image file: {image_path}")
#         else:
#             logger.error(f"Invalid image file: {image_file.filename}")
#             raise HTTPException(status_code=400, detail=f"Invalid image file: {image_file.filename}")

#     logger.info("Batch upload completed successfully.")
#     return JSONResponse(content={"message": "Files uploaded successfully", "uploaded_files": uploaded_files}, status_code=200)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)