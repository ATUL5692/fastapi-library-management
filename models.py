from database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, VARCHAR



class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(200), nullable = False)
    author= Column(String(200), nullable=False)
    isbn = Column(String(50), unique = True, nullable=False)
    category = Column(String(200), nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, default=0)
    shelf_location = Column(String(200), nullable=False)

class Members(Base):
    __tablename__= "member"

    member_id = Column(Integer, primary_key= True, index= True,unique=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    membership_date = Column(Date, nullable=False)
    status = Column(VARCHAR(20))

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer,ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(VARCHAR(20))
