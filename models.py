from database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime


# =========================
# BOOK
# =========================
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    isbn = Column(String(50), unique=True, nullable=False)
    category = Column(String(200), nullable=False)
    shelf_location = Column(String(200), nullable=False)
    pdf_url = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    transactions = relationship(
        "Transaction",
        back_populates="book",
        cascade="all, delete"
    )


# =========================
# USER
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    country_code = Column(String(5), nullable=False)
    phone = Column(String(15), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")

    created_at = Column(DateTime, default=datetime.utcnow)

    # composite uniqueness handled at DB level manually if needed

    # relationships
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete"
    )


# =========================
# TRANSACTION
# =========================
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    status = Column(String(20), default="issued")  # issued / expired

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    book = relationship("Book", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    # 🔥 IMPORTANT INDEX
    __table_args__ = (
        Index("idx_user_book_status", "user_id", "book_id", "status"),
    )