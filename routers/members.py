from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_members():
    return {"message": "Members working"}