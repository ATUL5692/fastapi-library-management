from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter()


@router.post("/")
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)


@router.get("/")
def get_books(db: Session = Depends(get_db)):
    return crud.get_books(db)


@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book_by_id(db, book_id)


@router.put("/{book_id}")
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.update_book(db, book_id, book)


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)

#For Members
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter()


@router.post("/")
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db, member)


@router.get("/")
def get_members(db: Session = Depends(get_db)):
    return crud.get_members(db)


@router.get("/{member_id}")
def get_member(member_id: int, db: Session = Depends(get_db)):
    return crud.get_member(db, member_id)


@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    return crud.delete_member(db, member_id)

#For transactions
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter()


@router.post("/borrow")
def borrow(data: schemas.BorrowBook, db: Session = Depends(get_db)):
    return crud.borrow_book(db, data)


@router.post("/return")
def return_book(data: schemas.BorrowBook, db: Session = Depends(get_db)):
    return crud.return_book(db, data.book_id, data.member_id)


#For book analytics
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
from database import get_db

router = APIRouter()


@router.get("/most-borrowed")
def most_borrowed(db: Session = Depends(get_db)):
    return crud.most_borrowed_books(db)


@router.get("/issued")
def issued(db: Session = Depends(get_db)):
    return crud.issued_books(db)


@router.get("/overdue")
def overdue(db: Session = Depends(get_db)):
    return crud.overdue_books(db)