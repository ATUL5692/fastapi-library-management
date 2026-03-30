from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta
from typing import List
from fastapi.responses import RedirectResponse
from urllib.parse import quote
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

    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
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

        return {"message": f"Access granted for {BORROW_DAYS} days"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already issued")

    except Exception as e:
        db.rollback()
        logging.error(str(e))
        raise HTTPException(status_code=500, detail="Issue failed")


# =========================
# READ BOOK (PRODUCTION SAFE)
# =========================
@router.get("/read/{book_id}")
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    # expire old access
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
            detail="Access expired or book not issued"
        )

    # get book
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or not book.pdf_url:
        raise HTTPException(status_code=404, detail="Book not found")

    # ✅ encode URL properly (VERY IMPORTANT)
    encoded_url = quote(book.pdf_url, safe="")

    viewer_url = f"https://docs.google.com/gview?url={encoded_url}&embedded=true"

    return RedirectResponse(viewer_url)


# =========================
# ISSUED BOOKS (ADMIN)
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
# EXPIRED BOOKS (ADMIN)
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