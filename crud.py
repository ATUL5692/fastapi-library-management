from sqlalchemy.orm import Session
import models
import schemas


def create_book(db: Session, book: schemas.BookCreate):
    new_book = models.Book(
        title = book.title,
        author = book.author,
        isbn = book.isbn,
        category = book.category,
        total_copies = book.total_copies
    )

    db.add(new_book)     
    db.commit()
    db.refresh(new_book)

    return new_book


def get_books(db: Session):
    return db.query(models.Book).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book == book_id).first()

def delete_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book == Book_id).first()

    if book:
        db.delete(book)
        db.commit()
    
    return book

def update_book()