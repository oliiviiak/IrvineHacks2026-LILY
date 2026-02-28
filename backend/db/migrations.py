# migrations.py
from db.db import db

MIGRATIONS = [
    # 000 - initial schema
    """
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        provider TEXT NOT NULL CHECK(provider IN ('apple', 'google', 'email')),
        subject TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE careneeders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        pfp TEXT,
        UNIQUE(user_id)
    );

    CREATE TABLE caretakers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        pfp TEXT,
        UNIQUE(user_id)
    );

    CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        member_id TEXT REFERENCES users(id),
        url TEXT,
        overview TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE document_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        line INTEGER NOT NULL,
        confidence REAL,
        content TEXT NOT NULL,
        UNIQUE(doc_id, line)
    );

    CREATE TABLE transcript_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        speaker TEXT,
        timestamp REAL,
        content TEXT NOT NULL
    );

    CREATE TABLE alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        transcript_id INTEGER REFERENCES transcript_items(id) ON DELETE SET NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE alert_document_lines (
        alert_id INTEGER NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
        doc_line_id INTEGER NOT NULL REFERENCES document_lines(id) ON DELETE CASCADE,
        PRIMARY KEY (alert_id, doc_line_id)
    );

    CREATE TABLE transcript_item_document_lines (
        transcript_item_id INTEGER NOT NULL REFERENCES transcript_items(id) ON DELETE CASCADE,
        doc_line_id INTEGER NOT NULL REFERENCES document_lines(id) ON DELETE CASCADE,
        PRIMARY KEY (transcript_item_id, doc_line_id)
    );
    """,
]
def migrate():
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

    applied = db.execute("SELECT COALESCE(MAX(version), -1) FROM _migrations").fetchone()[0]

    for i, sql in enumerate(MIGRATIONS):
        if i > applied:
            print(f"Applying migration {i}...")
            db.conn.executescript(sql)
            db.execute("INSERT INTO _migrations (version) VALUES (?)", (i,))
            db.commit()
            print(f"Migration {i} done.")

if __name__ == "__main__":
    migrate()