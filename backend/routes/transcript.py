from fastapi import APIRouter
from pydantic import BaseModel
from features.create_functions import create_transcript_item
from ai.ai import run

router = APIRouter(prefix="/transcript", tags=["transcript"])

class SendMessageRequest(BaseModel):
    convo_id: str
    content: str

@router.post("/")
def send_message(req: SendMessageRequest):
    create_transcript_item(
        convo_id=req.convo_id,
        speaker="careneeder",
        content=req.content
    )

    lily_response = run(req.content)

    create_transcript_item(
        convo_id=req.convo_id,
        speaker="LILY",
        content=lily_response
    )

    return {"response": lily_response}
