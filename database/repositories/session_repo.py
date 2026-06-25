class SessionRepository:
    def __init__(self, db):
        self.db = db

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def get_sessions_for_mouse(self, pyrat_id):
        return self.db.safe_query_all_dicts("""
            SELECT *
            FROM Session_data
            WHERE [Pyrat-ID] = ?
            ORDER BY [D.o.Recording], [T.o.Recording]
        """, (pyrat_id,))

    def get_all_experiments(self) -> list[str]:
        rows = self.db.safe_query_all_dicts("""
            SELECT DISTINCT Experiment
            FROM Session_data
            ORDER BY Experiment
        """)
        return [r["Experiment"] for r in rows] if rows else []

    def get_all_sessions(self):
        return self.db.safe_query_all_dicts("""
            SELECT *
            FROM Session_data
            ORDER BY [D.o.Recording], [T.o.Recording]
        """)

    def get_session_by_keys(self, pyrat_id, date, session_number):
        return self.db.safe_query_dict("""
            SELECT *
            FROM Session_data
            WHERE [Pyrat-ID] = ?
              AND [D.o.Recording] = ?
              AND CAST([Session_number] AS TEXT) = CAST(? AS TEXT)
        """, (pyrat_id, date, session_number))

    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------

    def insert_session(self, pyrat_id, experiment, session_number,
                       d_recording, t_recording, session, comment) -> bool:
        try:
            cur = self.db.conn.cursor()
            cur.execute("""
                INSERT INTO Session_data (
                    [Pyrat-ID], Experiment, Session_number,
                    [D.o.Recording], [T.o.Recording],
                    Session, Session_comment
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pyrat_id, experiment, session_number,
                d_recording, t_recording,
                session, comment
            ))

            self.db.conn.commit()
            return True

        except Exception:
            return False
