from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

import crud
import schemas
import models
from database import get_db

router = APIRouter()


# BORROW BOOK
@router.post("/borrow")
def borrow_book(data: schemas.BorrowBook, db: Session = Depends(get_db)):

    # Check if book exists
    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if user exists
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check availability
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")

    # Reduce stock
    book.available_copies -= 1

    # Create transaction
    transaction = models.Transaction(
        book_id=data.book_id,
        member_id=data.member_id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        status="issued"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "message": "Book borrowed successfully",
        "transaction_id": transaction.id
    }


#  RETURN BOOK 
@router.post("/return")
def return_book(data: schemas.BorrowBook, db: Session = Depends(get_db)):

    # Find active transaction
    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == data.book_id,
        models.Transaction.user_id == data.user_id,
        models.Transaction.return_date == None
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="No active borrow record found")

    # Set return date
    transaction.return_date = date.today()

    # Calculate fine
    delay = (transaction.return_date - transaction.due_date).days
    fine = delay * 10 if delay > 0 else 0
    transaction.fine = fine
    transaction.status = "returned"

    # Increase stock
    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    book.available_copies += 1

    db.commit()
    db.refresh(transaction)

    return {
        "message": "Book returned successfully",
        "fine": fine
    }


#  CURRENTLY ISSUED BOOKS 
@router.get("/issued")
def get_issued_books(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.return_date == None
    ).all()

    return transactions


# OVERDUE BOOKS 
@router.get("/overdue")
def get_overdue_books(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.return_date == None,
        models.Transaction.due_date < date.today()
    ).all()

    return transactions