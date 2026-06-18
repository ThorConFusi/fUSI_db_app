from database.db import Database, DatabaseError

class LoginRepository:
    def __init__(self, db: Database):
        self.db = db


    def get_credentials(self, surgeon: str):
        try:
            cur = self.db.safe_query("""
                SELECT Password, API_Base, API_Key
                FROM Login_data
                WHERE Surgeon = ?
            """, (surgeon,))
            row = cur.fetchone()
            if row:
                return row["Password"], row["API_Base"], row["API_Key"]
            return None, None, None
        except DatabaseError:
            return None, None, None


    # Load surgeons from DB
    def load_surgeons(self):
        try:
            cur = self.db.safe_query("SELECT Surgeon FROM Login_data")
            rows = cur.fetchall()
            return [row["Surgeon"] for row in rows] if rows else ["none available"]
        except DatabaseError:
            return ["none available"]
