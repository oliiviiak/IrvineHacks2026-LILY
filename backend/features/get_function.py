# backend/features/get_function.py
from db.db import db


def get_convo(convo_id: str):
    # All transcript items
    transcripts = [dict(r) for r in db.execute(
        "SELECT * FROM transcript_items WHERE convo_id = ? ORDER BY timestamp ASC",
        (convo_id,)
    ).fetchall()]

    # All documents
    documents = [dict(r) for r in db.execute(
        "SELECT * FROM documents WHERE convo_id = ? ORDER BY created_at ASC",
        (convo_id,)
    ).fetchall()]

    # All alerts across all documents in this convo
    alerts = []
    if documents:
        doc_ids = [d["document_id"] for d in documents]
        placeholders = ",".join("?" * len(doc_ids))
        alerts = [dict(r) for r in db.execute(
            f"SELECT * FROM alerts WHERE doc_id IN ({placeholders}) ORDER BY timestamp ASC",
            doc_ids
        ).fetchall()]

    return {
        "transcripts": transcripts,
        "alerts": alerts,
        "documents": documents,
    }