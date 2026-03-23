from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

import models
import schemas



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

def create_member(db: Session, member: schemas.MemberCreate):
    new_member = models.Member(
        name=member.name,
        email=member.email,
        phone=member.phone
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


def get_members(db: Session):
    return db.query(models.Member).all()


def get_member(db: Session, member_id: int):
    return db.query(models.Member).filter(models.Member.id == member_id).first()


def delete_member(db: Session, member_id: int):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        return None

    db.delete(member)
    db.commit()

    return member



# TRANSACTIONS

def borrow_book(db: Session, data: schemas.BorrowBook):

    book = db.query(models.Book).filter(models.Book.id == data.book_id).first()
    member = db.query(models.Member).filter(models.Member.id == data.member_id).first()
    if not book or not member:
        return None

    if book.available_copies <= 0:
        return {"error": "Book not available"}

    book.available_copies -= 1

    transaction = models.Transaction(
        member_id=data.member_id,
        book_id=data.book_id,
        issue_date=date.today(),
        due_date=date.today()
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def return_book(db: Session, book_id: int, member_id: int):

    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.member_id == member_id,
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
    return db.query(
        models.Transaction.book_id,
        func.count(models.Transaction.id).label("count")
    ).group_by(models.Transaction.book_id).all()


def issued_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None
    ).all()


def overdue_books(db: Session):
    return db.query(models.Transaction).filter(
        models.Transaction.return_date == None,
        models.Transaction.due_date < date.today()
    ).all()