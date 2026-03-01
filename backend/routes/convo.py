from fastapi import APIRouter
from pydantic import BaseModel
from db.db import create_convo

router = APIRouter(prefix="/convo", tags=["convo"])

class CreateConvoRequest(BaseModel):
    needer_id: str

@router.post("/")
def create_convo_route(req: CreateConvoRequest):
    convo_id = create_convo(req.careneeder_id)
    return {"convo_id": convo_id}
