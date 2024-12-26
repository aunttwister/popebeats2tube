"""
Database setup and models for the application.

This module initializes the database connection, defines ORM models, and provides
utility functions for managing database sessions.

Classes:
- Schedule: ORM model for the 'schedules' table.

Functions:
- get_db_session: Dependency function to get a database session.

Constants:
- SQLALCHEMY_DATABASE_URL: Connection string for the SQLite database.

Dependencies:
- SQLAlchemy: For ORM and database interaction.
- SQLite: File-based database used for this application.
"""

import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.services.config_mgmt_service import load_config

CONFIG = load_config("base")
DATABASE = CONFIG.get("db", "")
CONN_STR = DATABASE.get("conn_str", "")
# SQLite file-based database connection URL
SQLALCHEMY_DATABASE_URL = CONN_STR

# Create a database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured session factory for the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declare the base class for ORM models
Base = declarative_base()

class Schedule(Base):
    """
    Represents the 'schedules' table in the database.

    Attributes:
    - id (int): The primary key and unique identifier for each schedule.
    - date_created (datetime): The date and time when the schedule entry was created.
    - upload_date (datetime): The date and time when the schedule is set to be executed. Nullable.
    - executed (bool): Indicates whether the schedule has been executed.
    - video_title (str): The title of the video associated with the schedule.
    - image_location (str): The file path to the associated image.
    - audio_location (str): The file path to the associated audio.
    """
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(DateTime)
    upload_date = Column(DateTime, nullable=True)
    executed = Column(Boolean)
    video_title = Column(String)
    image_location = Column(String)
    audio_location = Column(String)
    
class User(Base):
    """
    Represents the 'users' table in the database.

    Attributes:
    - id (int): The primary key and unique identifier for each user.
    - email (str): The email address of the user. Must be unique.
    - youtube_api_key (str): The YouTube API key associated with the user.
    - date_created (datetime): The date and time when the user record was created.
    - is_active (bool): Indicates whether the user's account is active.
    """
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, nullable=False)
    youtube_api_key = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Dependency function to obtain a database session.

    Yields:
    - SessionLocal: An active database session for performing queries and transactions.
    
    Ensures that the session is properly closed after usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
