# migrations.py
from db.db import db

MIGRATIONS = [
    # 000 - initial schema
    """
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        provider TEXT NOT NULL CHECK(provider IN ('apple', 'google', 'email')),
        subject TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    );
    CREATE TABLE sessions (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    );
    CREATE TABLE careneeders (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        pfp TEXT,
        UNIQUE(user_id)
    );
    CREATE TABLE caretakers (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        pfp TEXT,
        UNIQUE(user_id)
    );
    CREATE TABLE conversations (
        convo_id TEXT PRIMARY KEY,
        needer_id TEXT NOT NULL REFERENCES careneeders(user_id)
    );
    CREATE TABLE documents (
        document_id TEXT PRIMARY KEY,
        convo_id TEXT NOT NULL REFERENCES conversations(convo_id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        url TEXT,
        overview TEXT,
        content TEXT
    );
    CREATE TABLE transcript_items (
        transcript_item_id TEXT PRIMARY KEY,
        convo_id TEXT NOT NULL REFERENCES conversations(convo_id) ON DELETE CASCADE,
        speaker TEXT,
        timestamp REAL,
        content TEXT NOT NULL
    );
    CREATE TABLE alerts (
        alert_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
        transcript_item_id TEXT REFERENCES transcript_items(transcript_item_id) ON DELETE SET NULL,
        timestamp TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        message TEXT NOT NULL
    );
    CREATE TABLE households (
        household_id TEXT PRIMARY KEY,
        name TEXT
    );
    CREATE TABLE household_members (
        household_id TEXT NOT NULL REFERENCES households(household_id) ON DELETE CASCADE,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        PRIMARY KEY (household_id, user_id)
    );
    """,
    
    # 001 - mock data for demo (fixed UUIDs so re-running is safe)
    """
    INSERT OR IGNORE INTO users (id, provider, subject) VALUES
        ('00000000-0000-0000-0000-000000000001', 'email', 'gertrude@demo.com'),
        ('00000000-0000-0000-0000-000000000002', 'email', 'carol@demo.com');

    INSERT OR IGNORE INTO careneeders (user_id, first_name, last_name) VALUES
        ('00000000-0000-0000-0000-000000000001', 'Gertrude', 'Washington');

    INSERT OR IGNORE INTO caretakers (user_id, first_name, last_name) VALUES
        ('00000000-0000-0000-0000-000000000002', 'Carol', 'Washington');

    INSERT OR IGNORE INTO households (household_id, name) VALUES
        ('00000000-0000-0000-0000-000000000010', 'Washington Family');

    INSERT OR IGNORE INTO household_members (household_id, user_id) VALUES
        ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001'),
        ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000002');
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