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


def create_document(convo_id: str, overview: str, content: str, url: str = None) -> str:
    document_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO documents (document_id, convo_id, url, overview, content) VALUES (?, ?, ?, ?, ?)",
        (document_id, convo_id, url, overview, content)
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


def create_household(name: str) -> str:
    household_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO households (household_id, name) VALUES (?, ?)",
        (household_id, name)
    )
    db.commit()
    return household_id


def add_household_member(household_id: str, user_id: str) -> None:
    db.execute(
        "INSERT INTO household_members (household_id, user_id) VALUES (?, ?)",
        (household_id, user_id)
    )
    db.commit()


def create_careneeder(user_id: str, first_name: str, last_name: str, pfp: str = None) -> None:
    db.execute(
        "INSERT INTO careneeders (user_id, first_name, last_name, pfp) VALUES (?, ?, ?, ?)",
        (user_id, first_name, last_name, pfp)
    )
    db.commit()


def create_caretaker(user_id: str, first_name: str, last_name: str, pfp: str = None) -> None:
    db.execute(
        "INSERT INTO caretakers (user_id, first_name, last_name, pfp) VALUES (?, ?, ?, ?)",
        (user_id, first_name, last_name, pfp)
    )
    db.commit()
