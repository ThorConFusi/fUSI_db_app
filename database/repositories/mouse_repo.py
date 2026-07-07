from database.db import Database


class MouseRepository:
    def __init__(self, db: Database):
        self.db = db

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def mouse_exists(self, pyrat_id: str) -> bool:
        row = self.db.safe_query_dict("""
            SELECT 1
            FROM Mouse_data
            WHERE [Pyrat-ID] = ?
        """, (pyrat_id,))
        return row is not None

    def get_alive_mice_ids(self) -> list[str]:
        rows = self.db.safe_query_all_dicts("""
            SELECT [Pyrat-ID]
            FROM Mouse_data
            WHERE TRIM(IFNULL([D.o.Death], '')) = ''
        """)
        return [r["Pyrat-ID"] for r in rows] if rows else []

    def get_mouse_by_id(self, pyrat_id: str) -> dict | None:
        return self.db.safe_query_dict("""
            SELECT *
            FROM Mouse_data
            WHERE [Pyrat-ID] = ?
        """, (pyrat_id,))

    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------

    def insert_mouse(self, pyrat_id, dob, sex, line, dos, tos, surgeon, license_) -> bool:
        try:
            cur = self.db.conn.cursor()
            cur.execute("""
                INSERT INTO Mouse_data (
                    [Pyrat-ID], [D.o.Birth], Sex, Line,
                    [D.o.Surgery], [T.o.Surgery],
                    Surgeon, License
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pyrat_id, dob, sex, line, dos, tos, surgeon, license_))

            self.db.conn.commit()
            return True

        except Exception:
            return False

    def kill_mouse(self, pyrat_id, dod, tod, method, purpose, comment) -> bool:
        try:
            cur = self.db.conn.cursor()
            cur.execute("""
                UPDATE Mouse_data
                SET [D.o.Death] = ?, [T.o.Death] = ?,
                    Kill_method = ?, Kill_purpose = ?, Kill_comment = ?
                WHERE [Pyrat-ID] = ?
            """, (dod, tod, method, purpose, comment, pyrat_id))

            self.db.conn.commit()
            return cur.rowcount > 0

        except Exception:
            return False

    def mark_mouse_uploaded(self, pyrat_id) -> bool:
        try:
            cur = self.db.conn.cursor()
            cur.execute("""
                UPDATE Mouse_data
                SET Mouse_in_RSpace = ?
                WHERE [Pyrat-ID] = ?
            """, (1, pyrat_id))

            self.db.conn.commit()
            return True

        except Exception:
            return False

    def mark_sacrifice_uploaded(self, pyrat_id) -> bool:
        try:
            cur = self.db.conn.cursor()
            cur.execute("""
                UPDATE Mouse_data
                SET Sacrifice_in_RSpace = ?
                WHERE [Pyrat-ID] = ?
            """, (1, pyrat_id))

            self.db.conn.commit()
            return True

        except Exception:
            return False
