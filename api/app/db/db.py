from datetime import datetime, timezone
from typing import Generator
import uuid
import subprocess
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import event
from app.db.custom_types import UtcDateTime
from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import logger

# Load configuration
CONFIG = load_config()
DATABASE = CONFIG.get("db", "")
CONN_STR = DATABASE.get("conn_str", "")

# MySQL database connection URL
SQLALCHEMY_DATABASE_URL = CONN_STR

# Create a database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Helps detect and recycle stale connections
    pool_size=5,         # Maintain a pool of connections
    max_overflow=10      # Maximum overflow connections beyond pool size
)

# Create a configured session factory for the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declare the base class for ORM models
Base = declarative_base()

class Tune(Base):
    """
    Represents the 'tunes' table in the database.
    """
    __tablename__ = 'tunes'

    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(UtcDateTime)
    upload_date = Column(UtcDateTime, nullable=True)
    executed = Column(Boolean)
    video_title = Column(String(255))
    base_dest_path = Column(String(512))
    img_name = Column(String(255))
    img_type = Column(String(64))
    audio_name = Column(String(255))
    audio_type = Column(String(64))
    tags = Column(String(1024))  # Store tags as a JSON-encoded string
    category = Column(String(128))
    privacy_status = Column(String(32))
    embeddable = Column(Boolean)
    license = Column(String(64))
    video_description = Column(String(1024))
    user_id = Column(String(36), ForeignKey('users.id'))

    # Backward relationship to User
    user = relationship("User", back_populates="tunes")


class User(Base):
    """
    Represents the 'users' table in the database.
    """
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False)
    youtube_access_token = Column(String(512), nullable=True)
    youtube_refresh_token = Column(String(512), nullable=True)
    youtube_token_expiry = Column(UtcDateTime, nullable=True)
    date_created = Column(UtcDateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Backward relationship to Tune
    tunes = relationship("Tune", back_populates="user")

# Initialize database schema using Alembic for migrations
def init_db():
    """
    Initializes the database schema using Alembic migrations.
    """
    try:
        logger.debug("Running Alembic migrations to initialize the database.")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.debug("Database initialized successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to initialize database via Alembic: {str(e)}")
        raise

def check_db_version():
    """
    Checks the current Alembic migration version in the database.

    Logs:
    -----
    - INFO: The current database schema version.
    - ERROR: If unable to fetch the database version.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            logger.info(f"Database schema is at version: {version}")
    except Exception as e:
        logger.error(f"Failed to retrieve database version: {str(e)}")
        raise

def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function to obtain a database session with logging.

    Yields:
    -------
    - SessionLocal: An active database session for performing queries and transactions.

    Logs:
    -----
    - DEBUG: Start and successful completion of session lifecycle.
    - ERROR: Failures in session handling.

    Ensures that the session is properly closed after usage.
    """
    logger.debug("Opening a new database session.")
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session committed successfully.")
    except Exception as e:
        logger.error(f"Database session rollback due to an error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed.")