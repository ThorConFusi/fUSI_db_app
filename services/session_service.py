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

    # ---------------------------------------------------------
    # Determine next session number (safe for GUI)
    # ---------------------------------------------------------
    def get_next_session_number_safe(self, pyrat_id):
        try:
            pyrat_id = validate_pyrat_id(pyrat_id)

            sessions = self.session_repo.get_sessions_for_mouse(pyrat_id)
            next_num = len(sessions) + 1

            return True, next_num

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    # ---------------------------------------------------------
    # Create a new session (called by AddSessionTab)
    # ---------------------------------------------------------
    def create_session(self, pyrat_id, experiment, sess_date, sess_time, session_type, comment=""):
        try:
            # Validation
            pyrat_id = validate_pyrat_id(pyrat_id)
            sess_date = validate_date(sess_date, "Session Date")
            sess_time = validate_time(sess_time, "Session Time")
            experiment = validate_dropdown(experiment, "Experiment")
            session_type = validate_dropdown(session_type, "Session Type")
            # comment darf leer sein

            # Mouse must exist
            mouse = self.session_repo.db.safe_query(
                "SELECT [Pyrat-ID] FROM Mouse_data WHERE [Pyrat-ID] = ?",
                (pyrat_id,)
            ).fetchone()

            if mouse is None:
                return False, "Mouse not found in database."

            # Determine next session number
            sessions = self.session_repo.get_sessions_for_mouse(pyrat_id)
            next_num = len(sessions) + 1

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

        # ---------------------------------------------------------
        # Insert into DB
        # ---------------------------------------------------------
        try:
            ok = self.session_repo.insert_session(
                pyrat_id,
                experiment,
                next_num,
                sess_date,
                sess_time,
                session_type,
                comment
            )

            if not ok:
                return False, "Database error while inserting session"

            return True, next_num

        except Exception as e:
            return False, f"Database error: {e}"

    # ---------------------------------------------------------
    # Get all sessions for a mouse
    # ---------------------------------------------------------
    def get_sessions_for_mouse(self, pyrat_id):
        try:
            pyrat_id = validate_pyrat_id(pyrat_id)
            sessions = self.session_repo.get_sessions_for_mouse(pyrat_id)
            return True, sessions
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    # ---------------------------------------------------------
    # Get all sessions
    # ---------------------------------------------------------
    def get_all_sessions(self):
        try:
            sessions = self.session_repo.get_all_sessions()
            return True, sessions
        except Exception:
            return True, []  # GUI must not crash

    # ---------------------------------------------------------
    # Get a single session
    # ---------------------------------------------------------
    def get_session_by_keys(self, pyrat_id, date, session_number):
        try:
            session = self.session_repo.get_session_by_keys(pyrat_id, date, session_number)
            return True, session
        except Exception:
            return False, {}

    # ---------------------------------------------------------
    # Get all experiment names (for dropdowns)
    # ---------------------------------------------------------
    def get_all_experiments(self) -> list[str]:
        try:
            exps = self.session_repo.get_all_experiments()
            return exps if exps else []
        except Exception:
            return []
