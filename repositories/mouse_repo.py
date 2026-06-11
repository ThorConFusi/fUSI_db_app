class MouseRepository:
    def __init__(self, db):
        self.db = db

    def insert_mouse(self, pyrat_id, dob, sex, line, dos, tos, surgeon, license_):
        self.db.safe_query("""
            INSERT INTO Mouse_data (
                [Pyrat-ID], [D.o.Birth], Sex, Line,
                [D.o.Surgery], [T.o.Surgery],
                Surgeon, License
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pyrat_id, dob, sex, line, dos, tos, surgeon, license_))

    def update_mouse_death(self, pyrat_id, dod, tod, method, purpose, comment):
        self.db.safe_query("""
            UPDATE Mouse_data
            SET [D.o.Death] = ?, [T.o.Death] = ?,
                Kill_method = ?, Kill_purpose = ?, Kill_comment = ?
            WHERE [Pyrat-ID] = ?
        """, (dod, tod, method, purpose, comment, pyrat_id))

    def get_mouse_by_id(self, pyrat_id):
        cur = self.db.safe_query("""
            SELECT *
            FROM Mouse_data
            WHERE [Pyrat-ID] = ?
        """, (pyrat_id,))
        row = cur.fetchone()
        return dict(row) if row else None


    def get_alive_mice_ids(self):
        cur = self.db.safe_query("""
            SELECT [Pyrat-ID]
            FROM Mouse_data
            WHERE [D.o.Death] IS NULL
        """)
        rows = cur.fetchall()
        return [r[0] for r in rows]
