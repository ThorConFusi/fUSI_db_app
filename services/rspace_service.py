from services.validators import validate_dropdown, ValidationError
from clients.rspace_client import RSpaceClient
import params


class RSpaceService:
    def __init__(self, login_repo, mouse_repo):
        self.login_repo = login_repo
        self.mouse_repo = mouse_repo
        self.logged_in = False
        self.current_surgeon = None
        self.client = None

    # ---------------------------------------------------------
    # LOGIN (to fetch APIkey and APIbase from DB)
    # ---------------------------------------------------------
    def check_login(self, surgeon: str, password: str):
        try:
            validate_dropdown(surgeon, "surgeon")
        except ValidationError as e:
            return False, None, str(e)

        if not password:
            return False, None, "Password cannot be empty"

        creds = self.login_repo.get_credentials(surgeon)
        if creds is None:
            return False, None, "No login data found for this surgeon"

        if creds.password != password:
            return False, None, "Incorrect password"

        if not creds.api_base or not creds.api_key:
            return False, None, "API configuration missing for this surgeon"

        api_base = creds.api_base.rstrip("/")
        if api_base.endswith("/api/v1"):
            api_base = api_base[:-7]
        api_base = api_base.rstrip("/")

        self.client = RSpaceClient(api_key=creds.api_key, url=api_base)

        ok, msg = self.client.check_connection()
        if not ok:
            return False, None, msg

        self.logged_in = True
        self.current_surgeon = surgeon
        return True, None, None

    # ---------------------------------------------------------
    # SURGEON LIST (to fill dropdown)
    # ---------------------------------------------------------
    def get_reg_surgeons(self):
        try:
            surgeons = self.login_repo.load_surgeons()
            return True, surgeons if surgeons else [], None
        except Exception as e:
            return False, [], f"Unexpected error: {e}"

    # ---------------------------------------------------------
    # UNIFIED EXPORT (always to Api Inbox)
    # ---------------------------------------------------------
    def export_to_rspace(self, data_dict: dict, comment: str | None,
                         folder_id: int, folder_type: str):
        if not self.logged_in:
            return False, None, "Not connected to RSpace"

        if self._determine_doc_type(data_dict) == "mouse":
            docname = self._build_mouse_docname(data_dict)
            doc_type = "mouse"
        elif self._determine_doc_type(data_dict) == "sacrifice":
            docname = self._build_sacrifice_docname(data_dict)
            doc_type = "sacrifice"
        else:
            docname = self._build_session_docname(data_dict)
            doc_type = "session"

        content = self._build_rspace_content(data_dict, comment, doc_type)

        try:
            result = self.client.upload_to_api_inbox(
                name=docname,
                content=content
            )
            short_msg = f"Uploaded to Api Inbox: '{result.get('name')}' (ID {result.get('id')})"
            return True, short_msg, None

        except Exception as e:
            return False, None, f"RSpace error: {e}"

    # ---------------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------------
    def _build_mouse_docname(self, data_dict: dict) -> str:
        pid = data_dict.get("Pyrat-ID", "unknown")
        return f"#{pid.replace('-', '')}"

    def _build_session_docname(self, data_dict: dict) -> str:
        date_raw = data_dict.get("D.o.Recording", "unknown_date")
        date = date_raw.replace("-", "")

        time_raw = data_dict.get("T.o.Recording", "unknown_time")
        time = time_raw.replace(":", "")

        number = str(data_dict.get("Session_number", "unknown_session"))
        experiment = data_dict.get("Experiment", "unknown_experiment")
        session_type = data_dict.get("Session", "unknown_type")

        return f"{date}_{time}_{number}_{experiment}_{session_type}"

    def _build_sacrifice_docname(self, data_dict: dict) -> str:
        date_raw = data_dict.get("D.o.Death", "unknown_date")
        date = date_raw.replace("-", "")

        time_raw = data_dict.get("T.o.Death", "unknown_time")
        time = time_raw.replace(":", "")

        method = data_dict.get("Kill_method", "unknown_method")

        return f"{date}_{time}_{method}"

    def _validate_keys(self, data_dict: dict, keys: list[str]) -> tuple[list[str], list[str]]:
        valid = []
        invalid = []

        for key in keys:
            if key in data_dict:
                valid.append(key)
            else:
                invalid.append(key)

        return valid, invalid

    def _determine_doc_type(self, data_dict: dict) -> str:
        if "D.o.Surgery" in data_dict:
            if data_dict["D.o.Death"] == None:
                return "mouse"
            else:
                return "sacrifice"
        return "session"

    # ---------------------------------------------------------
    # CONTENT BUILDER
    # ---------------------------------------------------------
    def _build_rspace_content(self, data_dict: dict, comment: str | None, doc_type: str):
        if not data_dict:
            return "<b>No data provided</b>"

        # Determine dokument type
        if doc_type == "mouse":
            keys = params.mouse_keys
            section_title = "Mouse Information"
        elif doc_type == "sacrifice":
            keys = params.sacrifice_keys
            section_title = "Sacrifice Information"
        else:
            keys = params.session_keys
            section_title = "Session Information"

        # Validate keys
        valid_keys, invalid_keys = self._validate_keys(data_dict, keys)

        html_parts = [f"<h2>{section_title}</h2>"]

        # Display valid keys only
        for key in valid_keys:
            html_parts.append(f"<b>{key}</b>: {data_dict.get(key, '—')}")

        # Display invalid keys (optional)
        if invalid_keys:
            html_parts.append("<br><h3>⚠️ Invalid Keys (not found in data)</h3>")
            html_parts.append(", ".join(invalid_keys))

        # Comment
        if comment:
            html_parts.append("<br><h2>Comment</h2>")
            html_parts.append(comment.strip())

        return "<br>".join(html_parts)
