# This file is for handling users part.


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from security import get_current_user

router = APIRouter()



# CREATE USER (ADMIN ONLY)

@router.post("/", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # TEMP: Only admin
    if current_user["user_id"] != 1:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check duplicate email
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check duplicate phone
    existing_phone = db.query(models.User).filter(
        models.User.phone == user.phone
    ).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already exists")

    return crud.create_user(db, user)



# GET ALL USERS (ADMIN ONLY)

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != 1:
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.get_users(db)



# GET USER BY ID

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = crud.get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# DELETE USER (ADMIN ONLY)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_id"] != 1:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check active transactions
    active_transaction = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.return_date == None
    ).first()

    if active_transaction:
        raise HTTPException(
            status_code=400,
            detail="User has active borrowed books and cannot be deleted"
        )


    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }