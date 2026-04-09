# Purpose: Data validation + response shaping

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date


# =========================
# AUTH
# =========================
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# BOOK
# =========================
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    pdf_url: str


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    category: str
    pdf_url: str

    class Config:
        from_attributes = True


# =========================
# USER
# =========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    country_code: str
    phone: str
    password: str

    @field_validator("country_code")
    def validate_country_code(cls, v):
        if not v.startswith("+") or not v[1:].isdigit():
            raise ValueError("Invalid country code")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) < 7 or len(v) > 15:
            raise ValueError("Invalid phone number")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    country_code: str
    phone: str
    role: str

    class Config:
        from_attributes = True


# =========================
# UPDATE NAME
# =========================
class UpdateName(BaseModel):
    name: str


# =========================
# UPDATE EMAIL
# =========================
class UpdateEmail(BaseModel):
    email: EmailStr


# =========================
# UPDATE PHONE
# =========================
class UpdatePhone(BaseModel):
    country_code: str
    phone: str

    @field_validator("country_code")
    def validate_country_code(cls, v):
        if not v.startswith("+") or not v[1:].isdigit():
            raise ValueError("Invalid country code")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) < 7 or len(v) > 15:
            raise ValueError("Invalid phone number")
        return v


# =========================
# CHANGE PASSWORD
# =========================
class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


# =========================
# BORROW SYSTEM
# =========================
class BorrowBook(BaseModel):
    book_id: int


class TransactionResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    issue_date: date
    due_date: date
    status: Optional[str] = None

    class Config:
        from_attributes = True