"""
This module defines endpoints for uploading tunes via FastAPI.

It includes two primary upload endpoints:
1. `/instant_upload/single`: For uploading a single tune.
2. `/instant_upload/batch`: For uploading a batch of tunes.

Each endpoint handles POST requests that accept tune data (either single or batch) and attempts to process the upload. If the upload is successful, a 200 response is returned; otherwise, a 400 error is raised.

Functions:
----------
- upload_single(tune: TuneDto): Handles the upload of a single tune.
- upload_batch(tunes: list[TuneDto]): Handles the upload of a batch of tunes.
"""


from fastapi import APIRouter, HTTPException
from app.dto import TuneDto
from app.utils.http_response_util import (
    response_200
)

instant_upload_router = APIRouter()

# /upload_tune/single - POST single tune upload
@instant_upload_router.post("/single")
async def upload_single(tune: TuneDto):
    """
    Handles the upload of a single tune.

    This endpoint accepts a `TuneDto` object that contains the details of a single tune. It processes the upload and responds with a success message if the upload is successful. If the upload fails, a 400 HTTP error is raised.

    Arguments:
    ----------
    - tune (TuneDto): The data transfer object that contains the details of the tune to be uploaded.

    Returns:
    --------
    - JSON response: A success message if the upload is successful.
    
    Raises:
    -------
    - HTTPException: 
    - 400: If the upload fails or the result is empty.
    """
    result: str
    #result = await upload_single_tune(tune)
    if not result:
        raise HTTPException(status_code=400, detail="Upload failed")
    return response_200("Upload successful")

# /upload_tune/batch - POST batch tune upload
@instant_upload_router.post("/batch")
async def upload_batch(tunes: list[TuneDto]):
    """
    Handles the upload of a batch of tunes.

    This endpoint accepts a list of `TuneDto` objects containing the details of multiple tunes. It processes the batch upload and responds with a success message if the upload is successful. If the upload fails, a 400 HTTP error is raised.

    Arguments:
    ----------
    - tunes (list[TuneDto]): A list of data transfer objects containing the details of multiple tunes to be uploaded.

    Returns:
    --------
    - JSON response: A success message if the batch upload is successful.

    Raises:
    -------
    - HTTPException:
    - 400: If the batch upload fails or the result is empty.
    """
    result: str
    #result = await upload_batch_tunes(tunes)
    if not result:
        raise HTTPException(status_code=400, detail="Batch upload failed")
    return response_200("Batch upload successful")