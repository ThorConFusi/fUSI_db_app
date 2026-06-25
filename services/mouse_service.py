from services.validators import (
    validate_pyrat_id,
    validate_date,
    validate_time,
    validate_dropdown,
    ValidationError
)


class MouseService:
    def __init__(self, mouse_repo):
        self.mouse_repo = mouse_repo


    # ---------------------------------------------------------
    # REGISTER MOUSE
    # ---------------------------------------------------------
    def register_mouse(self, pyrat_id, dob, sex, line, dos, tos, surgeon, license_):
        try:
            # Validation + Normalization
            pyrat_id = validate_pyrat_id(pyrat_id)
            dob      = validate_date(dob, "Date of Birth")
            sex      = validate_dropdown(sex, "Sex")
            line     = validate_dropdown(line, "Line")
            dos      = validate_date(dos, "Date of Surgery")
            tos      = validate_time(tos, "Time of Surgery")
            surgeon  = validate_dropdown(surgeon, "Surgeon")
            license_ = validate_dropdown(license_, "License")

            # Duplicate check
            if self.mouse_repo.mouse_exists(pyrat_id):
                return False, None, "Mouse already exists"

            # Insert
            ok = self.mouse_repo.insert_mouse(
                pyrat_id, dob, sex, line, dos, tos, surgeon, license_
            )

            if not ok:
                return False, None, "Database error while inserting mouse"

            return True, None, None

        except ValidationError as e:
            return False, None, str(e)

        except Exception as e:
            return False, None, f"Unexpected error: {e}"


    # ---------------------------------------------------------
    # KILL MOUSE
    # ---------------------------------------------------------
    def kill_mouse(self, pyrat_id, dod, tod, method, purpose, comment):
        try:
            pyrat_id = validate_pyrat_id(pyrat_id)
            dod      = validate_date(dod, "Date of Death")
            tod      = validate_time(tod, "Time of Death")
            method   = validate_dropdown(method, "Kill Method")
            purpose  = validate_dropdown(purpose, "Kill Purpose")
            # comment may be empty

            ok = self.mouse_repo.kill_mouse(
                pyrat_id, dod, tod, method, purpose, comment
            )

            if not ok:
                return False, None, "Mouse not updated (not found or DB error)"

            return True, None, None

        except ValidationError as e:
            return False, None, str(e)

        except Exception as e:
            return False, None, f"Unexpected error: {e}"


    # ---------------------------------------------------------
    # ALIVE MICE LISTS
    # ---------------------------------------------------------
    def get_alive_mice(self):
        mice = self.mouse_repo.get_alive_mice_ids()
        if not mice:
            return True, ["none available"], None
        return True, mice, None

    # ---------------------------------------------------------
    # EXPORT DATA
    # ---------------------------------------------------------
    def get_mouse_export_data(self, pyrat_id):
        try:
            pyrat_id = validate_pyrat_id(pyrat_id)
        except ValidationError as e:
            return False, None, str(e)

        mouse = self.mouse_repo.get_mouse_by_id(pyrat_id)

        if mouse is None:
            return False, None, f"Mouse '{pyrat_id}' not found"

        return True, mouse, None
