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
            validate_pyrat_id(pyrat_id)
            validate_date(dob, "Day of Birth")
            validate_dropdown(sex, "Sex")
            validate_dropdown(line, "Line")
            validate_date(dos, "Day of Surgery")
            validate_time(tos, "Time of Surgery")
            validate_dropdown(surgeon, "Surgeon")
            validate_dropdown(license_, "License")
        except Exception as e:
            return False, str(e)

        try:
            self.mouse_repo.insert_mouse(
                pyrat_id, dob, sex, line, dos, tos, surgeon, license_
            )
            return True, "Mouse stored"
        except Exception as e:
            return False, f"Database error: {e}"

    def kill_mouse(self, pyrat_id, dod, tod, method, purpose, comment):
        try:
            validate_pyrat_id(pyrat_id)
            validate_date(dod, "Day of Death")
            validate_time(tod, "Time of Death")
            validate_dropdown(method, "Kill method")
            validate_dropdown(purpose, "Kill purpose")

            # Comment obligatory when purpose "other"
            if purpose.lower() == "other" and not comment.strip():
                raise ValidationError("Please provide a comment when purpose is 'other'.")

            # Load mouse data
            mouse = self.mouse_repo.get_mouse_by_id(pyrat_id)
            if mouse is None:
                raise ValidationError("Mouse not found in database.")

            # Check if dead
            if mouse.get("D.o.Death"):
                raise ValidationError("Mouse is already marked as dead.")

            # Check if before birth
            dob = mouse.get("D.o.Birth")
            if dob and dod < dob:
                raise ValidationError("Day of Death cannot be before Day of Birth.")

            # Check if before surgery
            dos = mouse.get("D.o.Surgery")
            if dos and dod < dos:
                raise ValidationError("Day of Death cannot be before Day of Surgery.")

            # Check if in future
            from datetime import datetime
            today = datetime.today().strftime("%Y-%m-%d")
            if dod > today:
                raise ValidationError("Day of Death cannot be in the future.")

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

        # DB-Update
        try:
            self.mouse_repo.update_mouse_death(
                pyrat_id, dod, tod, method, purpose, comment
            )
            return True, "Mouse updated"
        except Exception as e:
            return False, f"Database error: {e}"


    def get_alive_mice_with_none(self) -> list[str]:
        """
        Returns a list of alive mice IDs plus 'none available'.
        Ensures dropdowns never break due to empty lists.
        """
        mice = self.mouse_repo.get_alive_mice_ids()

        if not mice:
            return ["none available"]

        return mice + ["none available"]

    def get_alive_mice(self):
        return self.mouse_repo.get_alive_mice_ids()


    def get_mouse_export_data(self, pyrat_id):
        mouse = self.mouse_repo.get_mouse_by_id(pyrat_id)
        if mouse is None:
            return False, "Mouse not found"
        return True, mouse
