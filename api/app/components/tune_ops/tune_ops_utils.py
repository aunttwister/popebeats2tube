from datetime import datetime, timezone
import json
from app.db.db import Tune
from app.dto import TuneDto


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