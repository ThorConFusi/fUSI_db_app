import params
import requests
from services.validators import validate_dropdown, ValidationError

class RSpaceService:
    def __init__(self, login_repo):
        self.login_repo = login_repo
        self.logged_in = False
        self.current_surgeon = None
        self.api_base = None
        self.api_key = None
        self.folder_id = params.rspace_folder_id

    def check_login(self, surgeon: str, password: str):
        try:
            validate_dropdown(surgeon, "surgeon")
        except ValidationError as e:
            return False, str(e)

        if not password:
            return False, "Password cannot be empty"

        stored_pw, api_base, api_key = self.login_repo.get_credentials(surgeon)

        if stored_pw is None:
            return False, "No login data found for this surgeon"

        if stored_pw != password:
            return False, "Incorrect password"

        if not api_base or not api_key:
            return False, "API configuration missing for this surgeon"

        # Login successful → set global Configuration
        self.logged_in = True
        self.current_surgeon = surgeon
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key

        return True, None

    def get_current_surgeon(self) -> str | None:
        return self.current_surgeon

    def export_mouse_to_rspace(self, mouse_data: dict, comment: str | None):
        if not self.logged_in:
            return False, "Not connected to RSpace"

        if not self.api_key or not self.api_base:
            return False, "RSpace API not configured"

        docname = "#" + mouse_data["Pyrat-ID"].replace("-", "")
        content = self._build_mouse_document(mouse_data, comment)

        url = f"{self.api_base}/documents"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": docname,
            "folderId": self.folder_id,
            "content": content,
            "type": "richtext"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
        except Exception as e:
            return False, f"Network error: {e}"

        if response.status_code not in (200, 201):
            return False, f"RSpace error {response.status_code}: {response.text}"

        return True, docname
