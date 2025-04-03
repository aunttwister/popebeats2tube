import asyncio
from app.db.db import User
from app.dto import TuneDto
from app.logger.logging_setup import logger
from app.services.file_transfer_service import transfer_files
from app.services.generate_mp4_service import generate_video
from app.services.tune2tube_service import upload_video
from app.utils.file_util import base64_to_file
from typing import List

CONCURRENCY_LIMIT = 3  # You can tune this

async def process_and_upload_tunes(tunes: List[TuneDto], user: User):
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def sem_task(tune):
        async with sem:
            await _process_and_upload_tune(tune, user)

    await asyncio.gather(*(sem_task(tune) for tune in tunes))

async def _process_and_upload_tune(tune: TuneDto, user: User):
    logger.debug(f"Processing tune '{tune.video_title}' for user '{user.id}'")

    try:
        audio_path, img_path, output_path = await asyncio.to_thread(_prepare_files, tune, user.id)

        logger.debug("Generating video...")
        mp4_path = await asyncio.to_thread(generate_video, audio_path, img_path, output_path, tune.video_title)
        logger.info(f"Generated video: {mp4_path}")

        logger.debug("Uploading to YouTube...")
        await asyncio.to_thread(
            upload_video,
            user.youtube_access_token,
            user.youtube_refresh_token,
            mp4_path,
            tune.video_title,
            tune.video_description,
            tune.category,
            tune.license,
            tune.embeddable,
            tune.privacy_status,
            tune.tags
        )

        logger.info(f"Upload complete: '{tune.video_title}'")
    except Exception as e:
        logger.error(f"Error processing tune '{tune.video_title}': {e}")
        raise

def _prepare_files(tune: TuneDto, user_id: str):
    audio_file = base64_to_file(tune.audio_file_base64, tune.audio_name)
    img_file = base64_to_file(tune.img_file_base64, tune.img_name)
    dest_path = transfer_files([audio_file, img_file], user_id, tune.video_title).replace("\\", "/")

    return (
        f"{dest_path}/{tune.audio_name}",
        f"{dest_path}/{tune.img_name}",
        f"{dest_path}/{tune.video_title}.mp4"
    )
