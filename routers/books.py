from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db

router = APIRouter()


# ------------------ CREATE BOOK ------------------
@router.post("/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):

    # Check duplicate ISBN
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

    return crud.create_book(db, book)


# ------------------ GET ALL BOOKS ------------------
@router.get("/", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return crud.get_books(db)


# ------------------ GET BOOK BY ID ------------------
@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):

    book = crud.get_book_by_id(db, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# ------------------ UPDATE BOOK ------------------
@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):

    # Check if book exists
    existing_book = crud.get_book_by_id(db, book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent duplicate ISBN (exclude current book)
    duplicate = db.query(models.Book).filter(
        models.Book.isbn == book.isbn,
        models.Book.id != book_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="ISBN already exists")

    updated_book = crud.update_book(db, book_id, book)
    return updated_book


# ------------------ DELETE BOOK ------------------
@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):

    # Check if book exists
    book = crud.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent deletion if book is currently issued
    issued = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.return_date == None
    ).first()

    if issued:
        raise HTTPException(status_code=400, detail="Book is currently issued and cannot be deleted")

    crud.delete_book(db, book_id)

    return {
        "message": "Book deleted successfully",
        "book_id": book_id
    }