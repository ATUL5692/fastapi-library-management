# Purpose: Data validation + response shaping

from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
import re


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


# USER (AUTH + PROFILE)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

    @field_validator("phone")
    def validate_phone(cls, value):
        pattern = r"^\+\d{1,3}\d{10}$"
        if not re.match(pattern, value):
            raise ValueError("Phone must be like '+917382936472'")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str


    class Config:
        from_attributes = True



# TRANSACTION


class TransactionCreate(BaseModel):
    book_id: int
    user_id: int


class TransactionResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
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
    user_id: int