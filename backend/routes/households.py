from fastapi import APIRouter
from pydantic import BaseModel
from features.create_functions import create_household, add_household_member

router = APIRouter(prefix="/household", tags=["household"])

class CreateHouseholdRequest(BaseModel):
    name: str

class AddMemberRequest(BaseModel):
    household_id: str
    user_id: str

@router.post("/")
def create_household_route(req: CreateHouseholdRequest):
    household_id = create_household(req.name)
    return {"household_id": household_id}

@router.post("/member")
def add_member_route(req: AddMemberRequest):
    add_household_member(req.household_id, req.user_id)
    return {"status": "ok"}
