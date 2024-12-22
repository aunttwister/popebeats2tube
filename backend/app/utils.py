"""
Utility functions for handling common operations used across the application.

This module includes functions for date validation and other shared utilities.
"""
from datetime import datetime

def is_past_date(upload_date: str) -> bool:
    """
    Check if the provided date string is in the past compared to the current date and time.

    Args:
        upload_date (str): The date string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

    Returns:
        bool: True if the provided upload date is in the past, False otherwise.
    
    Example:
        >>> is_past_date("2023-12-21T15:30:00")
        True
        >>> is_past_date("2025-01-01T00:00:00")
        False
    """
    return datetime.fromisoformat(upload_date) < datetime.now()
