from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from security import get_current_user, admin_only

router = APIRouter()


# =========================
# CREATE BOOK (ADMIN ONLY)
# =========================
@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()

    if existing:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

    return crud.create_book(db, book)


# =========================
# GET ALL BOOKS (ANY USER)
# =========================
@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Book).all()


# Search book by it's name.

@router.get("/search/", response_model=List[schemas.BookResponse])
def get_book_by_name(
    name: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    books = db.query(models.Book).filter(
        models.Book.title.ilike(f"%{name}%")
    ).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return books


# =========================
# GET BOOK BY ID
# =========================
@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book_by_id(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book







# =========================
# UPDATE BOOK (ADMIN ONLY)
# =========================
@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    existing_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    duplicate = db.query(models.Book).filter(
        models.Book.isbn == book.isbn,
        models.Book.id != book_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="ISBN already exists")

    return crud.update_book(db, book_id, book)


# =========================
# DELETE BOOK (ADMIN ONLY)
# =========================
@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent deletion if active users exist
    active = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.status == "issued"
    ).first()

    if active:
        raise HTTPException(
            status_code=400,
            detail="Book currently has active users"
        )

    db.delete(book)
    db.commit()

    return {
        "message": "Book deleted successfully",
        "book_id": book_id
    }