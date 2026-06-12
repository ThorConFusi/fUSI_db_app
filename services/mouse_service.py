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


    def register_mouse(self, pyrat_id, dob, sex, line, dos, tos, surgeon, license_):
        try:
            # Validierung + Normalisierung
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
                return False, "Mouse already exists"

            # Insert
            ok = self.mouse_repo.insert_mouse(
                pyrat_id, dob, sex, line, dos, tos, surgeon, license_
            )

            if not ok:
                return False, "Database error while inserting mouse"

            return True, "Mouse stored in database"

        except ValidationError as e:
            return False, str(e)

        except Exception as e:
            return False, f"Unexpected error: {e}"


    def kill_mouse(self, pyrat_id, dod, tod, method, purpose, comment):
        try:
            pyrat_id = validate_pyrat_id(pyrat_id)
            dod      = validate_date(dod, "Date of Death")
            tod      = validate_time(tod, "Time of Death")
            method   = validate_dropdown(method, "Kill Method")
            purpose  = validate_dropdown(purpose, "Kill Purpose")
            # comment darf leer sein → keine Validierung

            ok = self.mouse_repo.kill_mouse(
                pyrat_id, dod, tod, method, purpose, comment
            )

            if not ok:
                return False, "Mouse not updated (not found or DB error)"

            return True, "Mouse updated"

        except ValidationError as e:
            return False, str(e)

        except Exception as e:
            return False, f"Unexpected error: {e}"


    def get_alive_mice_with_none(self) -> list[str]:
        """
        Returns a list of alive mice IDs or 'none available'.
        Ensures dropdowns never break due to empty lists.
        """
        mice = self.mouse_repo.get_alive_mice_ids()
        return mice if mice else ["none available"]


    def get_alive_mice(self):
        """
        Returns a list of alive mice IDs and 'all'.
        Ensures dropdowns never break due to empty lists.
        """
        mice = self.mouse_repo.get_alive_mice_ids()
        return ["all"] + mice if mice else ["all"]


    def get_mouse_export_data(self, pyrat_id):
        mouse = self.mouse_repo.get_mouse_by_id(pyrat_id)
        if mouse is None:
            return False, "Mouse not found"
        return True, mouse
