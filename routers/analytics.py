from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

import models
from database import get_db

router = APIRouter()


# MOST BORROWED BOOKS 
@router.get("/most-borrowed")
def most_borrowed_books(db: Session = Depends(get_db)):

    result = db.query(
        models.Transaction.book_id,
        func.count(models.Transaction.id).label("borrow_count")
    ).group_by(models.Transaction.book_id)\
     .order_by(func.count(models.Transaction.id).desc())\
     .all()

    return result


#CURRENTLY ISSUED BOOKS
@router.get("/issued")
def issued_books(db: Session = Depends(get_db)):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.return_date == None
    ).all()

    return transactions


# OVERDUE BOOKS 
@router.get("/overdue")
def overdue_books(db: Session = Depends(get_db)):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.return_date == None,
        models.Transaction.due_date < date.today()
    ).all()

    return transactions


# TOTAL BOOKS COUNT 
@router.get("/total-books")
def total_books(db: Session = Depends(get_db)):

    count = db.query(func.count(models.Book.id)).scalar()

    return {"total_books": count}


#  TOTAL MEMBERS COUNT
@router.get("/total-members")
def total_members(db: Session = Depends(get_db)):

    count = db.query(func.count(models.Member.id)).scalar()

    return {"total_members": count}