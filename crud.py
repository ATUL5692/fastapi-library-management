# This file helps to talk to DB & implement logic.

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models
import schemas
from security import hash_password


# =========================
# BOOK CRUD
# =========================

def create_book(db: Session, book: schemas.BookCreate):
    new_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        category=book.category,
        pdf_url=book.pdf_url
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


def get_books(db: Session):
    return db.query(models.Book).all()


def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    existing_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not existing_book:
        return None

    existing_book.title = book.title
    existing_book.author = book.author
    existing_book.category = book.category
    existing_book.isbn = book.isbn
    existing_book.pdf_url = getattr(book, "pdf_url", None)

    db.commit()
    db.refresh(existing_book)

    return existing_book


def delete_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        return None

    db.delete(book)
    db.commit()

    return book


# =========================
# USER CRUD
# =========================

def create_user(db: Session, user: schemas.UserCreate):

    user_count = db.query(models.User).count()

    # First user = super_admin
    if user_count == 0:
        role = "super_admin"
    else:
        role = "user"

    hashed_pwd = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        country_code=user.country_code,
        phone=user.phone,
        password=hashed_pwd,
        role=role
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


# =========================
# ANALYTICS
# =========================

def most_borrowed_books(db: Session):
    results = db.query(
        models.Transaction.book_id,
        func.count(models.Transaction.id).label("count")
    ).group_by(models.Transaction.book_id).all()

    return [
        {"book_id": r.book_id, "count": r.count}
        for r in results
    ]


def issued_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.status == "issued"
    ).all()


def overdue_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.status == "expired"
    ).all()