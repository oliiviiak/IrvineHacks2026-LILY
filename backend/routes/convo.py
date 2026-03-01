# backend/routes/convo.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from features.create_functions import create_convo
from features.get_function import get_convo
from db.db import db

router = APIRouter(prefix="/convo", tags=["convo"])

class CreateConvoRequest(BaseModel):
    needer_id: str

@router.post("/")
def create_convo_route(req: CreateConvoRequest):
    convo_id = create_convo(req.needer_id)
    return {"convo_id": convo_id}

@router.get("/latest/{needer_id}")
def get_latest_convo(needer_id: str):
    row = db.execute(
        "SELECT * FROM conversations WHERE needer_id = ? ORDER BY rowid DESC LIMIT 1",
        (needer_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No conversations found")
    return dict(row)

@router.get("/{convo_id}")
def get_convo_route(convo_id: str):
    return get_convo(convo_id)