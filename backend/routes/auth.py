import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import features.auth as auth

router = APIRouter(prefix="/auth", tags=["document"])

class LoginRequest(BaseModel):
    provider: str
    oauth_code: str
    email: str

@router.post("/session")
async def create_session(req: LoginRequest):
    try:
        token = auth.Login(req.provider, req.oauth_code, req.email)
        return {"session_token": token}
    except:
        raise HTTPException(status_code=400, detail="unable to login")


@router.get("/session")
async def verify_session(current_user=Depends(auth.authenticate)):
    pass

@router.delete("/session")
async def delete_session(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    raw = base64.urlsafe_b64decode(credentials.credentials)

    auth.logout(raw)
