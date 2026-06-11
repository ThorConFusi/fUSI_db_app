from services.validators import (
    validate_pyrat_id,
    validate_date,
    validate_time,
    validate_dropdown,
    ValidationError
)

class SessionService:
    def __init__(self, session_repo):
        self.session_repo = session_repo


    def register_session(self, pyrat_id, d_recording, t_recording,
                         experiment, operator, comment=""):
        try:
            validate_pyrat_id(pyrat_id)
            validate_date(d_recording, "Session Date")
            validate_time(t_recording, "Session Time")
            validate_dropdown(experiment, "Experiment")
            validate_dropdown(operator, "Operator")

            # Maus must exist
            mouse = self.session_repo.db.safe_query(
                "SELECT [Pyrat-ID] FROM Mouse_data WHERE [Pyrat-ID] = ?",
                (pyrat_id,)
            ).fetchone()

            if mouse is None:
                raise ValidationError("Mouse not found in database.")

            # Session must not be in future
            from datetime import datetime
            today = datetime.today().strftime("%Y-%m-%d")
            if d_recording > today:
                raise ValidationError("Session Date cannot be in the future.")

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

        # Store in DB
        try:
            existing = self.session_repo.get_sessions_for_mouse(pyrat_id)
            session_number = str(len(existing) + 1)

            self.session_repo.insert_session(
                pyrat_id,
                experiment,
                session_number,
                d_recording,
                t_recording,
                experiment,
                comment
            )
            return True, "Session stored"

        except Exception as e:
            return False, f"Database error: {e}"


    def get_sessions_for_mouse(self, pyrat_id):
        try:
            validate_pyrat_id(pyrat_id)
        except Exception as e:
            return False, str(e)

        sessions = self.session_repo.get_sessions_for_mouse(pyrat_id)
        return True, sessions


    def get_all_sessions(self):
        try:
            sessions = self.session_repo.get_all_sessions()
            return True, sessions
        except Exception as e:
            # GUI must not crash → return empty list
            return True, []

    def get_session_by_keys(self, pyrat_id, date, session_number):
        try:
            session = self.session_repo.get_session_by_keys(pyrat_id, date, session_number)
            return True, session
        except Exception as e:
            print("get_session_by_keys ERROR:", e)
            return False, {}


    def get_all_experiments(self) -> list[str]:
        try:
            exps = self.session_repo.get_all_experiments()
            return exps if exps else []
        except Exception:
            return []
