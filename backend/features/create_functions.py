import uuid
import time
from db.db import db


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


def create_document(convo_id: str, overview: str, content: str) -> str:
    document_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO documents (document_id, convo_id, overview, content) VALUES (?, ?, ?, ?)",
        (document_id, convo_id, overview, content)
    )
    db.commit()
    return document_id


def create_transcript_item(convo_id: str, speaker: str, content: str) -> str:
    transcript_item_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO transcript_items (transcript_item_id, convo_id, speaker, timestamp, content) VALUES (?, ?, ?, ?, ?)",
        (transcript_item_id, convo_id, speaker, time.time(), content)
    )
    db.commit()
    return transcript_item_id