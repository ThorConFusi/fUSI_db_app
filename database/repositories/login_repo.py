from models.credentials import Credentials
from database.db import Database


class LoginRepository:
    def __init__(self, db):
        self.db = db

    def get_credentials(self, surgeon: str) -> Credentials | None:
        row = self.db.safe_query_dict("""
            SELECT Password AS password,
                   API_Base AS api_base,
                   API_Key AS api_key
            FROM Login_data
            WHERE Surgeon = ?
        """, (surgeon,))

        return Database.map_to_dataclass(Credentials, row)

    def load_surgeons(self) -> list[str]:
        rows = self.db.safe_query_all_dicts("SELECT Surgeon FROM Login_data")
        return [r["Surgeon"] for r in rows] if rows else []
