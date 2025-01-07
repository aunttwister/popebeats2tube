from sqlalchemy.types import TypeDecorator, DateTime
from datetime import datetime, timezone

class UtcDateTime(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        """Called when a value is being saved to the database."""
        if value is not None and value.tzinfo is None:
            raise ValueError("Naive datetime passed. Expected timezone-aware datetime.")
        return value

    def process_result_value(self, value, dialect):
        """Called when a value is retrieved from the database."""
        if value is not None and value.tzinfo is None:
            # Make naive datetime UTC-aware
            return value.replace(tzinfo=timezone.utc)
        return value