import requests


class RSpaceClient:
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

    def _get(self, path, params=None):
        resp = self._session.get(
            f"{self.base_url}/{path}",
            headers=self._headers,
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path, body):
        resp = self._session.post(
            f"{self.base_url}/{path}",
            headers=self._headers,
            json=body,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def check_connection(self):
        if not self.api_key:
            return False, "No API key entered."
        try:
            data = self._get("documents", {"pageSize": 1})
            return True, f"{self.url} ({data.get('totalHits', '?')} documents)"
        except Exception as exc:
            return False, str(exc)
