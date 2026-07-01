import requests
import params


class RSpaceClient:
    """
    Minimal client: all uploads go to Api Inbox (FL492620).
    """

    API_INBOX_ID = params.api_inbox_id

    def __init__(self, api_key, url, *, timeout=30, session=None):
        self.api_key = (api_key or "").strip()
        self.url = (url or "").rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    @property
    def base_url(self):
        return f"{self.url}/api/v1"

    @property
    def _headers(self):
        return {"apiKey": self.api_key, "Accept": "application/json"}

    # ------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------
    def _get(self, endpoint, params=None):
        r = self._session.get(
            f"{self.base_url}/{endpoint}",
            headers=self._headers,
            params=params,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint, json=None):
        r = self._session.post(
            f"{self.base_url}/{endpoint}",
            headers=self._headers,
            json=json,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------
    # Connection check
    # ------------------------------------------------------------
    def check_connection(self):
        if not self.api_key:
            return False, "No API key entered."

        try:
            data = self._get("documents", {"pageSize": 1})
            return True, f"{self.url} ({data.get('totalHits', '?')} documents)"
        except Exception as exc:
            return False, str(exc)

    # ---------------------------------------------------------
    # Upload ALWAYS to Api Inbox
    # ---------------------------------------------------------
    def upload_to_api_inbox(self, name, content):
        body = {
            "name": name,
            "parentFolderId": self.API_INBOX_ID,
            "fields": [
                {"content": f"<div>{content}</div>"}
            ],
        }

        r = self._session.post(
            f"{self.base_url}/documents",
            headers={"apiKey": self.api_key, "Accept": "application/json"},
            json=body,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()