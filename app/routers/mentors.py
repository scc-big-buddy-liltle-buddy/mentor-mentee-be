from fastapi import APIRouter
from app.db import get_all_object, db
from app.utils.matching import generate_match
from app.models import Mentor

router = APIRouter()

# Get 
@router.get("/list", tags=["mentors"])
async def get_all_mentors():
    mentors = get_all_object("mentors")
    return mentors

@router.get("/{id}", tags=["mentors"])
async def get_mentor_info(id: str):
    # Get data from firebase
    data = db.child("mentors").order_by_child("id").equal_to(id).get()
    if data.val() is None:
        return {}
    return data.val()

@router.post("/add", tags=["mentors"])
async def add_mentor(mentor: Mentor):
    data = mentor
    # Convert data to dictionary
    # data = data.dict()
    db.child("mentors").push(data)
    return {"message": "Mentor added!"}