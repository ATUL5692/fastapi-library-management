# This file helps to talk to DB & Implementing Logic.

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models
import schemas
from security import hash_password



# BOOK CRUD

def create_book(db: Session, book: schemas.BookCreate):
    new_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        category=book.category,
        total_copies=book.total_copies,
        available_copies=book.total_copies,
        shelf_location=book.shelf_location
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


def get_books(db: Session):
    return db.query(models.Book).all()


def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def delete_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        return None

    db.delete(book)
    db.commit()

    return book


def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    existing_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not existing_book:
        return None

    existing_book.title = book.title
    existing_book.author = book.author
    existing_book.category = book.category
    existing_book.total_copies = book.total_copies

    db.commit()
    db.refresh(existing_book)

    return existing_book



# MEMBER CRUD

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_users(db: Session):
    return db.query(models.User).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    db.delete(user)
    db.commit()

    return user



# TRANSACTIONS

def borrow_book(db: Session, data: schemas.BorrowBook):

    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not book or not user:
        return None

    if book.available_copies <= 0:
        return {"error": "Book not available"}

    book.available_copies -= 1

    transaction = models.Transaction(
        user_id=data.user_id,
        book_id=data.book_id,
        issue_date=date.today(),
        due_date=date.today()
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def return_book(db: Session, book_id: int, user_id: int):

    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.user_id == user_id,
        models.Transaction.return_date == None
    ).first()

    if not transaction:
        return {"error": "No active borrow record"}

    transaction.return_date = date.today()

    delay = (transaction.return_date - transaction.due_date).days
    transaction.fine = delay * 10 if delay > 0 else 0

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    book.available_copies += 1

    db.commit()
    db.refresh(transaction)

    return transaction



# ANALYTICS

def most_borrowed_books(db: Session):
    results = db.query(
        models.Transaction.book_id,
        func.count(models.Transaction.id).label("count")
    ).group_by(models.Transaction.book_id).all()

    return [
        {
            "book_id": r.book_id,
            "count": r.count
        }
        for r in results
    ]

def issued_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None
    ).all()


def overdue_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None,
        models.Transaction.due_date < date.today()
    ).all()