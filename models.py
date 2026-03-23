from database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship


#  BOOK 

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    isbn = Column(String(50), unique=True, nullable=False)
    category = Column(String(200), nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, default=0, nullable=False)
    shelf_location = Column(String(200), nullable=False)

    # relationship
    transactions = relationship("Transaction", back_populates="book")


#  MEMBER 

class Member(Base):
    __tablename__ = "members"  

    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    membership_date = Column(Date, nullable=True)
    status = Column(String(20), default="active")

    # relationship
    transactions = relationship("Transaction", back_populates="member")


#  TRANSACTION 

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)  

    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)

    fine = Column(Integer, default=0)
    status = Column(String(20), default="issued")

    # relationships
    book = relationship("Book", back_populates="transactions")
    member = relationship("Member", back_populates="transactions")