import re
import os
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error for service layer."""
    pass


# Normalization
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


# Date
def validate_date(value: str, field_name: str) -> str:
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"{field_name} must be in format YYYY-MM-DD")

    return value


# Time
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


# trial stimuli

def validate_bool(value, field_name: str) -> bool:
    """
    Accepts:
    - True / False
    - "True" / "False"
    - "" → False
    - None → False
    """
    if value in (True, "True"):
        return True
    if value in (False, "False", "", None):
        return False

    raise ValidationError(f"{field_name} must be True or False")


def validate_file(value: str, field_name: str, must_exist: bool = False) -> str:
    """
    Validates stimulation files:
    - Empty fields permitted
    - Path accepted
    - File names accepted
    - Optional: check for existence
    """
    if not value:
        return ""

    # Filenamen extrahieren
    filename = os.path.basename(value)

    if must_exist and not os.path.exists(value):
        raise ValidationError(f"{field_name}: file does not exist: {value}")

    return filename


def validate_duration(value: str) -> int:
    """
    Duration has to be a positive integer.
    """
    if value is None or value == "":
        raise ValidationError("duration_ms cannot be empty")

    try:
        ms = int(value)
    except ValueError:
        raise ValidationError("duration_ms must be an integer")

    if ms < 0:
        raise ValidationError("duration_ms must be >= 0")

    return ms


def validate_stimuli_row(row: dict) -> dict:
    """
    Validates a complete stimuli row.
    Expected Keys:
    pause, visual_stim, acoustic_stim, whisker_stim,
    odour_stim, air_puff, duration_ms
    """

    validated = {}

    validated["pause"] = validate_bool(row.get("pause"), "pause")
    validated["visual_stim"] = validate_file(row.get("visual_stim"), "visual_stim")
    validated["acoustic_stim"] = validate_file(row.get("acoustic_stim"), "acoustic_stim")
    validated["whisker_stim"] = validate_bool(row.get("whisker_stim"), "whisker_stim")
    validated["odour_stim"] = validate_bool(row.get("odour_stim"), "odour_stim")
    validated["air_puff"] = validate_bool(row.get("air_puff"), "air_puff")
    validated["duration_ms"] = validate_duration(row.get("duration_ms"))

    return validated
