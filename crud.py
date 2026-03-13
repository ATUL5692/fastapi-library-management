from sqlalchemy.orm import session
from models import Book, Members, Transaction
from schemas import BookCreate, MembersCreate

def create_book(db: session, book: schemas.BookCreate):
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



def get_books()