import asyncio
import os
from app.db.db import Tune, User
from app.logger.logging_setup import logger
from app.components.file_processing.file_processing_service import get_audio_path, get_image_path
from app.components.ffmpeg.generate_mp4.generate_mp4_service import generate_video
from app.components.tune_ops.tune_ops_service import mark_tune_as_executed_service
from app.components.upload.tune2tube.tune2tube_service import upload_video
from typing import List
from app.settings.env_settings import YOUTUBE_ACCESS_CONCURRENCY_LIMIT
from app.db.db import get_db_session

async def process_and_upload_tunes(tunes: List[Tune], user: User):
    sem = asyncio.Semaphore(YOUTUBE_ACCESS_CONCURRENCY_LIMIT)

    async def sem_task(tune):
        async with sem:
            await _process_and_upload_tune(tune, user)

    await asyncio.gather(*(sem_task(tune) for tune in tunes))

async def _process_and_upload_tune(tune: Tune, user: User):
    logger.debug(f"Processing tune '{tune.video_title}' for user '{user.id}'")
    try:
        audio_path = get_audio_path(tune)
        img_path = get_image_path(tune)

        logger.debug("Generating video...")
        mp4_path = await asyncio.to_thread(generate_video, audio_path, img_path, tune.base_dest_path, tune.video_title)
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
        
        db = next(get_db_session())

        await mark_tune_as_executed_service(tune, db)
    except Exception as e:
        logger.error(f"Error processing tune '{tune.video_title}': {e}")
        if(os.path.exists(mp4_path)):
            os.remove(mp4_path)
        raise
