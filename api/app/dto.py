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
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.logging.logging_setup import logger

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

class ScheduleDto(BaseModel):
    """
    Data Transfer Object (DTO) for a Schedule.
    """
    id: Optional[int] = None
    date_created: Optional[datetime] = None
    upload_date: datetime
    executed: bool
    video_title: str
    img_file: Optional[str] = None
    img_name: str
    img_type: str
    audio_file: Optional[str] = None
    audio_name: str
    audio_type: str
    tags: Optional[list[str]] = Field(default_factory=list)
    category: Optional[str] = None
    privacy_status: str = Field(default="private")
    embeddable: bool = Field(default=False)
    license: str = Field(default="youtube")
    video_description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        str_min_length=0,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
    @field_validator('upload_date')
    @classmethod
    def validate_upload_date(cls, value):
        """
        Ensure that the upload date is timezone-aware.
        Raises a ValueError if the upload date is invalid.
        """
        try:
            if isinstance(value, str):
                # Parse string to datetime if needed
                value = datetime.fromisoformat(value)
            if value.tzinfo is None:
                # Make the datetime timezone-aware if it's naive
                value = value.replace(tzinfo=timezone.utc)
            return value
        except Exception as e:
            raise ValueError(f"Invalid upload_date: {value}. Error: {e}")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, value):
        """
        Ensure that tags are always a list.
        """
        if not isinstance(value, list):
            raise ValueError("Tags must be a list.")
        return value
