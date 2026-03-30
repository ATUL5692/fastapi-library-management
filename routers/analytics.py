# This file is for Book Analysis part

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

import models
import schemas
from database import get_db
from security import get_current_user, admin_only

router = APIRouter()


# =========================
# MOST BORROWED BOOKS
# =========================
@router.get("/most-borrowed")
def most_borrowed_books(
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_only)
):
    result = db.query(
        models.Transaction.book_id,
        func.count(models.Transaction.id).label("borrow_count")
    ).group_by(models.Transaction.book_id)\
     .order_by(func.count(models.Transaction.id).desc())\
     .all()

    return [
        {
            "book_id": r.book_id,
            "borrow_count": r.borrow_count
        }
        for r in result
    ]


# =========================
# ISSUED BOOKS
# =========================
@router.get("/issued", response_model=List[schemas.TransactionResponse])
def issued_books(
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_only)
):
    return db.query(models.Transaction).filter(
        models.Transaction.status == "issued"
    ).all()


# =========================
# TOTAL BOOKS
# =========================
@router.get("/total-books")
def total_books(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    count = db.query(func.count(models.Book.id)).scalar()
    return {"total_books": count}


# =========================
# TOTAL USERS
# =========================
@router.get("/total-users")
def total_users(
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_only)
):
    count = db.query(func.count(models.User.id)).scalar()
    return {"total_users": count}