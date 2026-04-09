from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
from fastapi.responses import RedirectResponse
import logging

import schemas
import models
from database import get_db
from security import get_current_user, admin_only

router = APIRouter()

BORROW_DAYS = 7

logging.basicConfig(level=logging.INFO)


# =========================
# HELPER: AUTO EXPIRE
# =========================
def expire_transactions(db: Session):
    db.query(models.Transaction).filter(
        models.Transaction.status == "issued",
        models.Transaction.due_date < date.today()
    ).update({"status": "expired"}, synchronize_session=False)


# =========================
# ISSUE BOOK (USER)
# =========================
@router.post("/issue")
def issue_book(
    data: schemas.BorrowBook,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    expire_transactions(db)
    db.commit()

    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    existing = db.query(models.Transaction).filter(
        models.Transaction.book_id == data.book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Book already issued")

    transaction = models.Transaction(
        book_id=data.book_id,
        user_id=user_id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=BORROW_DAYS),
        status="issued"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    logging.info(f"User {user_id} issued book {data.book_id}")

    return {
        "message": f"Access granted for {BORROW_DAYS} days",
        "book_id": data.book_id
    }


# =========================
# RETURN BOOK
# =========================
@router.post("/return/{book_id}")
def return_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="No active issue found")

    transaction.status = "returned"
    db.commit()

    return {"message": "Book returned successfully"}


# =========================
# READ BOOK (FIXED CORE LOGIC)
# =========================
@router.get("/read/{book_id}")
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    # expire outdated transactions
    expire_transactions(db)
    db.commit()

    # check access
    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=403,
            detail="Access denied (not issued or expired)"
        )

    # get book
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or not book.pdf_url:
        raise HTTPException(status_code=404, detail="Book not found")

    # REDIRECT (clean)
    return RedirectResponse(url=book.pdf_url)


# =========================
# ADMIN: ISSUED
# =========================
@router.get("/issued", response_model=List[schemas.TransactionResponse])
def get_issued_books(
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_only)
):
    expire_transactions(db)
    db.commit()

    return db.query(models.Transaction).filter(
        models.Transaction.status == "issued"
    ).all()


# =========================
# ADMIN: EXPIRED
# =========================
@router.get("/expired", response_model=List[schemas.TransactionResponse])
def get_expired_books(
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_only)
):
    expire_transactions(db)
    db.commit()

    return db.query(models.Transaction).filter(
        models.Transaction.status == "expired"
    ).all()