from pydantic import BaseModel
from datetime import date



# BOOK

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    shelf_location: str


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    available_copies: int
    shelf_location: str

    class Config:
        from_attributes = True



# MEMBER
class MemberCreate(BaseModel):
    name: str
    email: str
    phone: str


class MemberResponse(BaseModel):
    id: int 
    name: str
    email: str
    phone: str
    membership_date: date | None
    status: str | None

    class Config:
        from_attributes = True



# TRANSACTION
class TransactionCreate(BaseModel):
    book_id: int
    member_id: int


class TransactionResponse(BaseModel):
    id: int   # ✅ FIXED (not transaction_id)
    book_id: int
    member_id: int
    issue_date: date
    due_date: date
    return_date: date | None
    fine: int | None
    status: str | None

    class Config:
        from_attributes = True



# BORROW

class BorrowBook(BaseModel):
    book_id: int
    member_id: int