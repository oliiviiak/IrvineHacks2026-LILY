from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["profile"])

class CreateProfileRequest(BaseModel):
    first_name: str
    last_name: str

@router.post("/")
async def create_profile(req: CreateProfileRequest):
    return {"status": "ok"}


