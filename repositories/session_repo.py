class SessionRepository:
    def __init__(self, db):
        self.db = db

    def insert_session(self, pyrat_id, experiment, session_number,
                       d_recording, t_recording, session, comment):

        self.db.safe_query("""
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

    def get_sessions_for_mouse(self, pyrat_id):
        cur = self.db.safe_query("""
            SELECT *
            FROM Session_data
            WHERE [Pyrat-ID] = ?
            ORDER BY [D.o.Recording], [T.o.Recording]
        """, (pyrat_id,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_all_experiments(self) -> list[str]:
        cur = self.db.safe_query("""
            SELECT DISTINCT Experiment
            FROM Session_data
            ORDER BY Experiment
        """)
        rows = cur.fetchall()
        return [r[0] for r in rows]

    def get_all_sessions(self):
        cur = self.db.safe_query("""
            SELECT *
            FROM Session_data
            ORDER BY [D.o.Recording], [T.o.Recording]
        """)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


    def get_session_by_keys(self, pyrat_id, date, session_number):
        cur = self.db.safe_query("""
            SELECT *
            FROM Session_data
            WHERE [Pyrat-ID] = ?
            AND [D.o.Recording] = ?
            AND CAST([Session_number] AS TEXT) = CAST(? AS TEXT)
        """, (pyrat_id, date, session_number))

        row = cur.fetchone()
        return dict(row) if row else {}
