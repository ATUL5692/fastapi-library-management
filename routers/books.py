from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db
from security import get_current_user

router = APIRouter()



# DEPENDENCIES

def admin_only(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


def user_only(user: dict = Depends(get_current_user)):
    return user



# CREATE BOOK (ADMIN ONLY)

@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(admin_only)
):
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

    return crud.create_book(db, book)



# GET ALL BOOKS (ANY USER)

@router.get("/", response_model=List[schemas.BookResponse])
def get_books(
    db: Session = Depends(get_db),
    user: dict = Depends(user_only)
):
    return crud.get_books(db)



# GET BOOK BY ID (ANY USER)

@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(user_only)
):
    book = crud.get_book_by_id(db, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# UPDATE BOOK (ADMIN ONLY)

@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(admin_only)
):
    existing_book = crud.get_book_by_id(db, book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent duplicate ISBN
    duplicate = db.query(models.Book).filter(
        models.Book.isbn == book.isbn,
        models.Book.id != book_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="ISBN already exists")

    return crud.update_book(db, book_id, book)



# DELETE BOOK (ADMIN ONLY)

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(admin_only)
):
    book = crud.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent deletion if issued
    issued = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.return_date == None
    ).first()

    if issued:
        raise HTTPException(
            status_code=400,
            detail="Book is currently issued and cannot be deleted"
        )

    crud.delete_book(db, book_id)

    return {
        "message": "Book deleted successfully",
        "book_id": book_id
    }