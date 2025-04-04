from datetime import datetime, timezone
from typing import List, Tuple

from app.db.db import Tune
from app.logger.logging_setup import logger
from requests import Session

from app.dto import TuneDto
from app.repositories.instant_tune_repository import insert_instant_tunes_batch
from app.services.file_processing_service import cleanup_temp_files, persistence_preparation_processing, processing_commit
from app.services.schedule_tune_service import map_tune_dto_to_model

async def validate_and_create_instant_batch_service(tunes: List[TuneDto], user_id: str, db: Session) -> List[Tune]:
    db_tunes = []
    temp_paths = []
    file_mappings: List[Tuple[str, str]] = []

    logger.debug(f"Starting batch validation and preparation for {len(tunes)} tunes (user_id={user_id})")

    try:
        for tune in tunes:
            logger.debug(f"Validating tune: '{tune.video_title}'")

            logger.debug(f"Preparing persistence paths for tune: '{tune.video_title}'")
            audio_map, img_map, base_dest_path = persistence_preparation_processing(tune, user_id)

            temp_paths.extend([audio_map[0], img_map[0]])
            file_mappings.extend([audio_map, img_map])

            logger.debug(f"Mapped tune '{tune.video_title}' to DB model with base path: {base_dest_path}")
            db_tunes.append(map_tune_dto_to_model(tune, user_id, base_dest_path=base_dest_path))

        logger.debug(f"Inserting {len(db_tunes)} tunes into the database...")
        created_tunes = await insert_instant_tunes_batch(db_tunes, db)

        logger.debug("Database insert successful. Committing file move operations...")
        processing_commit(file_mappings)

        logger.info(f"Batch upload successfully validated, saved, and processed for user_id={user_id}")
        return created_tunes

    except Exception as e:
        logger.error(f"Batch creation failed: {str(e)}")
        cleanup_temp_files(temp_paths)
        raise