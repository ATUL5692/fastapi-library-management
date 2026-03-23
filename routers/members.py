from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db

router = APIRouter()


#  CREATE MEMBER 
@router.post("/", response_model=schemas.MemberResponse)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):

    # Check duplicate email
    existing_email = db.query(models.Member).filter(
        models.Member.email == member.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check duplicate phone
    existing_phone = db.query(models.Member).filter(
        models.Member.phone == member.phone
    ).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already exists")

    return crud.create_member(db, member)


# GET ALL MEMBERS 
@router.get("/", response_model=list[schemas.MemberResponse])
def get_members(db: Session = Depends(get_db)):
    return crud.get_members(db)


#  GET MEMBER BY ID 
@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):

    member = crud.get_member(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


#  DELETE MEMBER 
@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):

    # Check if member exists
    member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Check active transactions
    active_transaction = db.query(models.Transaction).filter(
        models.Transaction.member_id == member_id,
        models.Transaction.return_date == None
    ).first()

    if active_transaction:
        raise HTTPException(
            status_code=400,
            detail="Member has active borrowed books and cannot be deleted"
        )

    # Delete member
    db.delete(member)
    db.commit()

    return {
        "message": "Member deleted successfully",
        "member_id": member_id
    }