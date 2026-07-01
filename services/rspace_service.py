from services.validators import validate_dropdown, ValidationError
from clients.rspace_client import RSpaceClient


class RSpaceService:
    def __init__(self, login_repo, mouse_repo):
        self.login_repo = login_repo
        self.mouse_repo = mouse_repo
        self.logged_in = False
        self.current_surgeon = None
        self.client = None

    # ---------------------------------------------------------
    # LOGIN
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
    # SURGEON LIST
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

        print("DEBUG data_dict:", type(data_dict), data_dict)
        print("DEBUG comment:", comment)

        if not self.logged_in:
            return False, None, "Not connected to RSpace"

        # Maus oder Session?
        if "D.o.Surgery" in data_dict:
            docname = self._build_mouse_docname(data_dict)
        else:
            docname = self._build_session_docname(data_dict)

        content = self._build_rspace_content(data_dict, comment)

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
    # CONTENT BUILDER
    # ---------------------------------------------------------
    def _build_rspace_content(self, data_dict: dict, comment: str | None):

        print("DEBUG building content from:", type(data_dict), data_dict)

        if not data_dict:
            return "<b>No data provided</b>"

        mouse_keys = [
            "Pyrat-ID", "Sex", "Line", "D.o.Birth",
            "D.o.Surgery", "T.o.Surgery",
            "D.o.Death", "T.o.Death",
            "Kill_method", "Kill_purpose", "Kill_comment"
        ]

        session_keys = [
            "D.o.Recording", "T.o.Recording",
            "Session_number", "Experiment", "Session"
        ]

        html_parts = []

        html_parts.append("<h2>Mouse Information</h2>")
        for key in mouse_keys:
            html_parts.append(f"<b>{key}</b>: {data_dict.get(key, '—')}")

        html_parts.append("<br><h2>Session Information</h2>")
        for key in session_keys:
            html_parts.append(f"<b>{key}</b>: {data_dict.get(key, '—')}")

        if comment:
            html_parts.append("<br><h2>Comment</h2>")
            html_parts.append(comment.strip())

        return "<br>".join(html_parts)

    # ---------------------------------------------------------
    # DOCUMENT NAME BUILDERS
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
