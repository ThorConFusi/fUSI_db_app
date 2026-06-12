import re
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error for service layer."""
    pass


# Normalisierung
def _normalize_pyrat_id(pid: str | None) -> str | None:
    if pid is None:
        return None

    # Remove spaces
    pid = pid.strip()
    if pid == "":
        return None

    # Unicode-Dashes to ASCII-Minus
    pid = pid.replace("–", "-").replace("—", "-")

    # All caps
    pid = pid.upper()

    return pid


# Pyrat-ID
def validate_pyrat_id(pyrat_id: str) -> str:
    pid = _normalize_pyrat_id(pyrat_id)

    if not pid:
        raise ValidationError("Pyrat ID cannot be empty")

    if not re.match(r"^[A-Z]{3}-[A-Z0-9]{4}$", pid):
        raise ValidationError("Pyrat ID must follow the format AAA-XXXX")

    return pid


# Datum
def validate_date(value: str, field_name: str) -> str:
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"{field_name} must be in format YYYY-MM-DD")

    return value


# Uhrzeit
def validate_time(value: str, field_name: str) -> str:
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if not re.match(pattern, value):
        raise ValidationError(f"{field_name} must be in hh:mm format (00:00–23:59)")

    return value


# Dropdowns
def validate_dropdown(value: str, field_name: str) -> str:
    if not value or value == "none available":
        raise ValidationError(f"Please select a valid {field_name}")

    return value
