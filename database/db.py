import sqlite3

DB_PATH = "fUSI_sessions.db"

class DatabaseError(Exception):
    pass

class Database:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Login_data (
                Surgeon   TEXT,
                Password  TEXT,
                [API_base] TEXT,
                [API_key]  TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Mouse_data (
                [Pyrat-ID]    TEXT,
                [D.o.Birth]   TEXT,
                Sex           TEXT,
                Line          TEXT,
                [D.o.Surgery] TEXT,
                [T.o.Surgery] TEXT,
                Surgeon       TEXT,
                License       TEXT,
                [D.o.Death]   TEXT,
                [T.o.Death]   TEXT,
                Kill_method   TEXT,
                Kill_purpose  TEXT,
                Kill_comment  TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Session_data (
                [Pyrat-ID]      TEXT,
                Experiment      TEXT,
                Session_number  TEXT,
                [D.o.Recording] TEXT,
                [T.o.Recording] TEXT,
                Session         TEXT,
                Session_comment TEXT
            )
        """)

        self.conn.commit()

    def table_exists(self, table_name: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table_name,))
        return cur.fetchone() is not None

    def safe_query(self, query, params=()):
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur
        except sqlite3.Error as e:
            raise DatabaseError(f"DB error: {e}")
