from database.db import Database


class LoginRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_credentials(self, surgeon: str):
        row = self.db.safe_query_dict("""
            SELECT Password, API_Base, API_Key
            FROM Login_data
            WHERE Surgeon = ?
        """, (surgeon,))

        if row:
            return row["Password"], row["API_Base"], row["API_Key"]
        return None, None, None

    def load_surgeons(self):
        rows = self.db.safe_query_all_dicts("SELECT Surgeon FROM Login_data")
        return [r["Surgeon"] for r in rows] if rows else ["none available"]
