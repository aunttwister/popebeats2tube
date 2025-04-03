from datetime import datetime, timezone
import json
import os
from typing import List, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.db.db import Tune
from app.dto import TuneDto
from app.repositories.schedule_tune_repository import (
    delete_tune_by_id,
    get_tune_by_id,
    get_tunes,
    insert_tunes_batch,
    update_tune_fields
)
from app.logger.logging_setup import logger
from app.services.file_transfer_service import generate_file_path
from app.utils.file_util import base64_to_file, delete_directory
from app.services.temp_file_mgmt_service import save_temp_file, move_temp_file, cleanup_temp_files


async def get_user_tunes_service(user_id: str, page: int, limit: int, db: Session) -> Tuple[list, int]:
    logger.debug(f"Fetching tunes from DB for user: {user_id}, page: {page}, limit: {limit}")
    tunes_list, tunes_total_count = await get_tunes(db, user_id, page, limit)
    logger.debug(f"Retrieved {len(tunes_list)} out of total {tunes_total_count} tunes for user_id: {user_id}")

    return tunes_list, tunes_total_count 


async def validate_and_create_batch_service(tunes: List[TuneDto], user_id: str, db: Session):
    current_time = datetime.now(timezone.utc)
    db_tunes = []
    temp_paths = []
    file_mappings: List[Tuple[str, str]] = []  # (temp_path, final_path)

    try:
        for tune in tunes:
            if not tune.upload_date:
                raise ValueError(f"Upload date is missing for {tune.video_title}")
            if tune.upload_date < current_time:
                raise ValueError(f"Upload date is in the past for {tune.video_title}")

            # Decode base64 into UploadFile-like objects
            img_file: UploadFile = base64_to_file(tune.img_file_base64, f"{tune.video_title}.{tune.img_type}")
            audio_file: UploadFile = base64_to_file(tune.audio_file_base64, f"{tune.video_title}.{tune.audio_type}")

            # Save to temp
            img_temp_path = save_temp_file(img_file)
            audio_temp_path = save_temp_file(audio_file)
            temp_paths.extend([img_temp_path, audio_temp_path])

            # Generate final path
            final_dir = generate_file_path(user_id, tune.video_title)

            img_final_path = os.path.join(final_dir, img_file.filename)
            audio_final_path = os.path.join(final_dir, audio_file.filename)
            file_mappings.append((img_temp_path, img_final_path))
            file_mappings.append((audio_temp_path, audio_final_path))

            db_tunes.append(map_tune_dto_to_model(tune, user_id, base_dest_path=final_dir))

        created_tunes = await insert_tunes_batch(db_tunes, db)

        # Move files only after successful DB insert
        for temp_path, final_path in file_mappings:
            move_temp_file(temp_path, final_path)

        return created_tunes

    except Exception as e:
        cleanup_temp_files(temp_paths)
        logger.error(f"Batch creation failed: {str(e)}")
        raise

def map_tune_dto_to_model(tune: TuneDto, user_id: str, base_dest_path: str) -> Tune:
    return Tune(
        upload_date=tune.upload_date,
        executed=tune.executed,
        video_title=tune.video_title,
        base_dest_path=base_dest_path,
        img_name=tune.img_name,
        img_type=tune.img_type,
        audio_name=tune.audio_name,
        audio_type=tune.audio_type,
        date_created=datetime.now(timezone.utc),
        user_id=user_id,
        privacy_status=tune.privacy_status,
        embeddable=tune.embeddable,
        license=tune.license,
        category=tune.category,
        tags=json.dumps(tune.tags),
        video_description=tune.video_description,
    )



async def validate_and_update_tune_service(tune_id: int, tune: TuneDto, db: Session) -> TuneDto:
    if tune.upload_date < datetime.now(timezone.utc):
        raise ValueError("Upload date is in the past")

    existing = await get_tune_by_id(tune_id, db)
    if not existing:
        raise LookupError("Tune not found")

    return await update_tune_fields(tune_id, tune, db)


async def delete_user_tune_service(tune_id: int, db: Session) -> bool:
    existing = await get_tune_by_id(tune_id, db)
    if not existing:
        raise LookupError("Tune not found")

    if existing.base_dest_path:
        delete_directory(existing.base_dest_path)

    return await delete_tune_by_id(tune_id, db)
