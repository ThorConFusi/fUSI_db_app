import sqlite3
from database.db import DatabaseError


class MouseRepository:
    def __init__(self, db):
        self.db = db

    # ---------------------------------------------------------
    # SELECT (read from DB)
    # ---------------------------------------------------------
    def mouse_exists(self, pyrat_id: str) -> bool:
        cur = self.db.safe_query(
            "SELECT 1 FROM Mouse_data WHERE [Pyrat-ID] = ?",
            (pyrat_id,)
        )
        return cur.fetchone() is not None


    def get_alive_mice_ids(self) -> list[str]:
        cur = self.db.safe_query("""
            SELECT [Pyrat-ID]
            FROM Mouse_data
            WHERE TRIM(IFNULL([D.o.Death], '')) = ''
        """)
        return [row[0] for row in cur.fetchall()]


    def get_mouse_by_id(self, pyrat_id: str) -> dict | None:
        cur = self.db.safe_query("""
            SELECT *
            FROM Mouse_data
            WHERE [Pyrat-ID] = ?
        """, (pyrat_id,))
        row = cur.fetchone()
        return dict(row) if row else None


    # ---------------------------------------------------------
    # WRITE (Upload to DB)
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

        except Exception as e:
            print("DB INSERT ERROR:", e)
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

            # Check for row change
            return cur.rowcount > 0

        except Exception as e:
            print("DB UPDATE ERROR:", e)
            return False
