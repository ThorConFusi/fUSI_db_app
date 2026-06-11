import re
from datetime import datetime

class ValidationError(Exception):
    """Custom validation error for service layer."""
    pass

def validate_pyrat_id(pyrat_id: str):
    if not pyrat_id:
        raise ValidationError("Pyrat ID cannot be empty")

    if not re.match(r"^[A-Za-z]{3}-\d{4}$", pyrat_id):
        raise ValidationError("Pyrat ID must follow the format AAA-xxxx")


def validate_date(value: str, field_name: str):
    """
    Validates a date string in YYYY-MM-DD format.
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"{field_name} must be in format YYYY-MM-DD")

    return True


def validate_time(value: str, field_name: str):
    """
    Validates a time string in hh:mm format (24h).
    Accepts 00:00 to 23:59.
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    # Regex for 24h time format
    pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"

    if not re.match(pattern, value):
        raise ValidationError(f"{field_name} must be in hh:mm format (00:00–23:59)")

    return True


def validate_dropdown(value: str, field_name: str):
    if not value or value == "none available":
        raise ValidationError(f"Please select a valid {field_name}")
