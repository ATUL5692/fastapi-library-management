from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas, crud
from database import get_db
from security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================
# REGISTER
# =========================
@router.post("/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing = crud.get_user_by_email(db, user.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists. Please login."
        )

    new_user = crud.create_user(db, user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )

    # 🔥 FIXED TOKEN STRUCTURE (IMPORTANT)
    token = create_access_token({
        "sub": str(db_user.id),   # always string
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }