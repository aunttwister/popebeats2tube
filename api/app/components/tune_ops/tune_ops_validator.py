from datetime import datetime, timezone
from typing import List
from app.dto import TuneDto
from app.logger.logging_setup import logger

def validate_scheduled_tunes_upload_time(tunes: List[TuneDto]):
    current_time = datetime.now(timezone.utc)
    for tune in tunes:
        logger.debug(f"Validating tune: '{tune.video_title}'")

        if not tune.upload_date:
            raise ValueError(f"Upload date is missing for '{tune.video_title}'")
        if tune.upload_date < current_time:
            raise ValueError(f"Upload date is in the past for '{tune.video_title}'")