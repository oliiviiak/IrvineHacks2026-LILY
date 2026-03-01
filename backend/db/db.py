# db.py
import sqlite3
from pathlib import Path
import uuid

DB_PATH = Path("./db/app.db")

class Database:
    _instance: "Database | None" = None

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")

    @classmethod
    def get(cls) -> "Database":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def executemany(self, sql: str, params: list[tuple]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, params)

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

db = Database.get()


def create_convo(needer_id: str) -> str:
    convo_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO conversations (convo_id, needer_id) VALUES (?, ?)",
        (convo_id, needer_id)
    )
    db.commit()
    return convo_id


def create_alert(doc_id: str, message: str, transcript_item_id: str = None) -> str:
    alert_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO alerts (alert_id, doc_id, transcript_item_id, message) VALUES (?, ?, ?, ?)",
        (alert_id, doc_id, transcript_item_id, message)
    )
    db.commit()
    return alert_id