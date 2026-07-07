import sqlite3
from dataclasses import fields


DB_PATH = "fUSI_sessions.db"


class DatabaseError(Exception):
    pass


class Database:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    # ---------------------------------------------------------
    # TABLE CREATION
    # ---------------------------------------------------------
    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Login_data (
                Surgeon    TEXT,
                Password   TEXT,
                [API_base] TEXT,
                [API_key]  TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Mouse_data (
                [Pyrat-ID]          TEXT,
                [D.o.Birth]         TEXT,
                Sex                 TEXT,
                Line                TEXT,
                [D.o.Surgery]       TEXT,
                [T.o.Surgery]       TEXT,
                Mouse_in_RSpace     INTEGER DEFAULT (0),
                Surgeon             TEXT,
                License             TEXT,
                [D.o.Death]         TEXT,
                [T.o.Death]         TEXT,
                Sacrifice_in_RSpace INTEGER DEFAULT (0),
                Kill_method         TEXT,
                Kill_purpose        TEXT,
                Kill_comment        TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Session_data (
                [Pyrat-ID]          TEXT,
                Experiment          TEXT,
                Session_number      TEXT,
                [D.o.Recording]     TEXT,
                [T.o.Recording]     TEXT,
                Session_in_RSpace   INTEGER DEFAULT (0),
                Session             TEXT,
                Session_comment     TEXT
            )
        """)

        self.conn.commit()

    # ---------------------------------------------------------
    # SAFE SELECT QUERIES
    # ---------------------------------------------------------
    def safe_query(self, query, params=()):
        """Execute a SELECT query and return the cursor."""
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur
        except sqlite3.Error as e:
            raise DatabaseError(f"DB error: {e}")

    def safe_query_dict(self, query: str, params=()) -> dict | None:
        """Return a single row as a dictionary, or None."""
        cur = self.safe_query(query, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def safe_query_all_dicts(self, query: str, params=()) -> list[dict]:
        """Return all rows as a list of dictionaries."""
        cur = self.safe_query(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    # ---------------------------------------------------------
    # DATACLASS MAPPING
    # ---------------------------------------------------------
    @staticmethod
    def map_to_dataclass(model_cls, row: dict):
        if row is None:
            return None
        kwargs = {f.name: row.get(f.name) for f in fields(model_cls)}
        return model_cls(**kwargs)
