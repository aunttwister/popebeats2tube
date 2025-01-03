"""
This module contains Data Transfer Objects (DTOs) for the application. DTOs are used 
to structure and validate data that flows between different layers of the application, 
such as the database, services, and API endpoints. The models in this module ensure 
data integrity and type safety throughout the application.

Classes:
    TuneDto: Represents the data structure for tune-related operations.
    ScheduleDto: Represents the data structure for schedule-related operations.
"""

from typing import Optional
from fastapi import UploadFile
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreateDTO(BaseModel):
    email: EmailStr

class AuthRequestDto(BaseModel):
    """
    Data Transfer Object for handling authentication requests.

    Attributes:
    ----------
    token : str
        The authentication token, typically received from a third-party provider (e.g., Google OAuth token).
    """
    token: str

class TuneDto(BaseModel):
    """
    Data Transfer Object (DTO) for a Tune.

    Attributes:
        id (int): The unique identifier of the tune.
        title (str): The title of the tune.
        description (str): A description of the tune.
        audio_file (str): The file path or file name of the audio file.
        image_file (str): The file path or file name of the associated image.
    """
    id: int
    title: str
    description: str
    audio_file: str
    image_file: str
    
class FileDto(BaseModel):
    """
    DTO for a file.
    
    Attributes:
        file (str): The base64-encoded file data.
        type (str): The file type or extension (e.g., 'png', 'mp3').
    """
    file: str
    type: str

class ScheduleDto(BaseModel):
    """
    Data Transfer Object (DTO) for a Schedule.

    Attributes:
        id (int): The unique identifier of the schedule.
        date_created (datetime): The timestamp when the schedule was created.
        upload_date (Optional[datetime]): The scheduled date for upload, if specified.
        executed (bool): Indicates whether the schedule has been executed.
        video_title (str): The title of the video associated with the schedule.
        image_location (str): The file path or file name of the associated image.
        audio_location (str): The file path or file name of the associated audio.
    """
    id: Optional[int] = None
    date_created: Optional[datetime] = None
    upload_date: datetime
    executed: bool
    video_title: str
    img: Optional[FileDto] = Field(default=None)  # Optional for retrieval
    audio: Optional[FileDto] = Field(default=None)  # Optional for retrieval
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace = True,
        str_min_length = 0,
        use_enum_values = True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        })

    @field_validator('upload_date')
    @classmethod
    def validate_upload_date(cls, v):
        """
        Ensure that the upload date is in the future and is timezone-aware.
        Raises a ValueError if the upload date is in the past.
        """
        if v:
            # Make the datetime timezone-aware if it's naive
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v < datetime.now(timezone.utc):
                raise ValueError("Upload date must be in the future.")
        return v
