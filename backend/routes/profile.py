from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from features.create_functions import create_careneder, create_caretaker
import features.auth as auth

router = APIRouter(prefix="/profile", tags=["profile"])

class CreateProfileRequest(BaseModel):
    first_name: str
    last_name: str
    role: str
    pfp: str = None

@router.post("/")
async def create_profile(req: CreateProfileRequest, user_id: str = Depends(auth.authenticate)):
    if req.role == "careneder":
        create_careneder(user_id, req.first_name, req.last_name, req.pfp)
    elif req.role == "caretaker":
        create_caretaker(user_id, req.first_name, req.last_name, req.pfp)
    else:
        raise HTTPException(status_code=400, detail="role must be careneeder or caretaker")
    
    return {"status": "ok"}
