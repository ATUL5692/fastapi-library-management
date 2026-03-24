from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db

router = APIRouter()


#  CREATE USER
@router.post("/", response_model=schemas.UserResponse)
def create_user(member: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check duplicate email
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check duplicate phone
    existing_phone = db.query(models.Member).filter(
        models.User.phone == user.phone
    ).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already exists")

    return crud.create_user(db, user)


# GET ALL USERS 
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


#  GET USER BY ID 
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = crud.get_member(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


#  DELETE USER 
@router.delete("/{user_id}")
def delete_user(member_id: int, db: Session = Depends(get_db)):

    # Check if user exists
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

    # Delete member
    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }