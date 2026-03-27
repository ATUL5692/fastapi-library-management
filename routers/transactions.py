# This file is for book transactions part.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
import schemas
import models
from database import get_db
from security import get_current_user, admin_only

router = APIRouter()


# BORROW BOOK (USER)

@router.post("/borrow")
def borrow_book(
    data: schemas.BorrowBook,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    # Check book exists
    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check already borrowed
    existing = db.query(models.Transaction).filter(
        models.Transaction.book_id == data.book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.return_date == None
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Book already borrowed by user")

    # Check availability
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")

    try:
        # Reduce stock
        book.available_copies -= 1

        # Create transaction
        transaction = models.Transaction(
            book_id=data.book_id,
            user_id=user_id,
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

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Borrow failed")



# RETURN BOOK (USER)

@router.post("/return")
def return_book(
    data: schemas.BorrowBook,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == data.book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.return_date == None
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="No active borrow record found")

    try:
        # Set return date
        transaction.return_date = date.today()

        # Fine calculation
        delay = (transaction.return_date - transaction.due_date).days
        fine = delay * 10 if delay > 0 else 0

        transaction.fine = fine
        transaction.status = "returned"

        # Increase stock (use relation)
        book = transaction.book
        book.available_copies += 1

        db.commit()
        db.refresh(transaction)

        return {
            "message": "Book returned successfully",
            "fine": fine
        }

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Return failed")



# ISSUED BOOKS (ADMIN ONLY)

@router.get("/issued", response_model=List[schemas.TransactionResponse])
def get_issued_books(
    db: Session = Depends(get_db),
    user: dict = Depends(admin_only)
):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None
    ).all()




# OVERDUE BOOKS (ADMIN ONLY)

@router.get("/overdue", response_model=List[schemas.TransactionResponse])
def get_overdue_books(
    db: Session = Depends(get_db),
    user: dict = Depends(admin_only)
):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None,
        models.Transaction.due_date < date.today()
    ).all()