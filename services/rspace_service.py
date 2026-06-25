import params
from services.validators import validate_dropdown, ValidationError
from clients.rspace_client import RSpaceClient


class RSpaceService:
    def __init__(self, login_repo, mouse_repo):
        self.login_repo = login_repo
        self.mouse_repo = mouse_repo
        self.logged_in = False
        self.current_surgeon = None
        self.client = None
        self.folder_id = params.rspace_mice_folder_id

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

        # API-Base normalisieren
        api_base = creds.api_base.rstrip("/")
        if not api_base.endswith("/api/v1"):
            api_base = api_base + "/api/v1"
        api_base = api_base.replace("/api/v1", "")  # Client hängt /api/v1 selbst an

        # RSpaceClient erzeugen
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
    # CURRENT SURGEON
    # ---------------------------------------------------------
    def get_current_surgeon(self):
        return True, self.current_surgeon, None

    # ---------------------------------------------------------
    # EXPORT
    # ---------------------------------------------------------
    def export_mouse_to_rspace(self, data_dict: dict, comment: str | None):
        if not self.logged_in:
            return False, None, "Not connected to RSpace"

        # Dokumentname: #TEST836 statt Mouse_TES-T836
        pyrat_id = data_dict.get("Pyrat-ID", "unknown")
        docname = f"#{pyrat_id.replace('-', '')}"

        # Inhalt: HTML mit allen Feldern + Kommentar
        content = self._build_rspace_content(data_dict, comment)
        if not content.strip():
            return False, None, "No content to upload"

        body = {
            "name": docname,
            "folderId": self.folder_id,  # z.B. "FL248822"
            "content": f"<div>{content}</div>",
            "type": "richtext"
        }

        try:
            result = self.client._post("documents", body)
        except Exception as e:
            return False, None, f"RSpace error: {e}"

        # Erfolgsmeldung kürzen
        short_msg = f"Uploaded to RSpace: {result.get('name')} (ID {result.get('id')})"
        return True, short_msg, None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _build_rspace_content(self, data_dict: dict, comment: str | None):
        if not data_dict:
            return "<b>No data provided</b>"

        # Mouse- und Session-Daten trennen
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

        # HTML-Abschnitte erzeugen
        html_parts = []

        # Mouse Information
        html_parts.append("<h2>Mouse Information</h2>")
        for key in mouse_keys:
            value = data_dict.get(key, "—")
            html_parts.append(f"<b>{key}</b>: {value}")

        # Session Information
        html_parts.append("<br><h2>Session Information</h2>")
        for key in session_keys:
            value = data_dict.get(key, "—")
            html_parts.append(f"<b>{key}</b>: {value}")

        # Kommentar
        if comment:
            html_parts.append("<br><h2>Comment</h2>")
            html_parts.append(comment.strip())

        # Alles zusammenfügen
        return "<br>".join(html_parts)

