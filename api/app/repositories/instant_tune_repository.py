from typing import List

from requests import Session

from app.db.db import Tune


async def insert_instant_tunes_batch(tunes: List[Tune], db: Session) -> List[Tune]:
    """
    Create multiple tunes in a single database transaction.

    Args:
    -----
    tunes : List[TuneDto]
        The list of tune details to create.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    List[TuneDto]
        The list of created tunes mapped to DTO objects.

    Logs:
    -----
    - DEBUG: Start and completion of batch tune creation.
    - INFO: Details of the created tunes.
    - ERROR: Failures during the batch operation.
    """
    created_tunes = []
    try:
        db.add_all(tunes)
        db.commit()

        created_tunes = tunes
        for tune in created_tunes:
            db.refresh(tune)
        return created_tunes
    except Exception as e:
        db.rollback()
        raise Exception(f"Error occurred during batch creation of tunes: {str(e)}")