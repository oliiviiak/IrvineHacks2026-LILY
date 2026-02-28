from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/document", tags=["document"])

class CreateDocumentRequest(BaseModel):
    image: str
    audio: str

@router.post("/")
async def create_document(req: CreateDocumentRequest):
    
    return {"status": "ok"}

