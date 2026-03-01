import base64
import uuid

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from db.db import db
import os
import hashlib

def login(provider: str, oauth_code: str, local_email: str) -> str:

    match provider:
        case "email":
            id = getUser(provider, local_email)
            if id == None:
                id = createUser(provider, local_email)

        case "google":
            pass
        case "apple":
            pass

    if id == None:
        raise ValueError("Invalid authentication")

    return createSession(id)

def logout(token: bytes) -> bool:
    token_hash = hash_token(token)
    res = db.execute(
        "DELETE FROM sessions WHERE token_hash = ?",
        (token_hash.hex(),)
    )
    db.commit()

    if res.rowcount == 0:
        raise ValueError("Session not found")


def getUser(provider: str, subject: str) -> str | None:
    query = """
        SELECT * FROM users
        WHERE provider = ?
        AND subject = ?
        LIMIT 1
    """
    
    row = db.execute(query, (provider, subject)).fetchone()
    if row is None:
        return None

    return row["id"]

bearer_scheme = HTTPBearer()
def authenticate(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    raw = base64.urlsafe_b64decode(credentials.credentials)
    token_hash = hash_token(raw)

    query = """
        SELECT * FROM sessions WHERE token_hash = ? LIMIT 1
    """

    row = db.execute(query, (token_hash.hex(),)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return row["user_id"]

def createUser(provider: str, subject: str) -> str | None:
    query = """
        INSERT INTO users (id, provider, subject) VALUES (?, ?, ?)
    """

    user_id = str(uuid.uuid7())
    res = db.execute(query, (user_id, provider, subject))
    if res.rowcount == 0:
        return None

    db.commit()

    return user_id

def createSession(id: str) -> str:
    query = """     
        INSERT INTO sessions (user_id, token_hash) VALUES (?, ?)
    """
    token, tokenHash = create_session_token()


    res = db.execute(query, (id, tokenHash.hex()))
    if res.rowcount == 0:
        print("failed to create session")
    
    db.commit()
    token = base64.urlsafe_b64encode(token).decode()

    return token




def create_session_token() -> tuple[bytes, bytes]:
    raw = os.urandom(32)
    hash_ = hash_token(raw)
    return raw, hash_

def hash_token(raw: bytes) -> bytes:
    return hashlib.sha256(raw).digest()