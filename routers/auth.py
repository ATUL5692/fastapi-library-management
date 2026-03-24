from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from security import verify_password
import models, schemas, crud
from database import get_db

router = APIRouter()


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing = crud.get_user_by_email(db, user.email)

    if existing:
        return {
            "message": "User already exists. Please login.",
            "action": "login"
        }

    new_user = crud.create_user(db, user)

    return {
        "message": "User registered successfully",
        "action": "login",
        "user_id": new_user.id
    }


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {"message": "Login successful"}