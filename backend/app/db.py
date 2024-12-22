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

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file-based database connection URL
SQLALCHEMY_DATABASE_URL = "sqlite:\\192.168.1.100\D$\database\sqlite\popebeats2tube.dev"

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
