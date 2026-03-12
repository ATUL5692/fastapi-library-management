from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine
import pymysql
from dotenv import load_dotenv
import os
from datetime import date, datetime

DATABASE_URL = "mysql+pymysql://root:M%40ngo112@localhost/library_db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(200), nullable = False)
    author= Column(String(200), nullable=False)
    isbn = Column(String(50), unique = True, nullable=False)
    category = Column(String(200), nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer,default=0)
    shelf_location = Column(String(200),nullable=False)

class Members(Base):
    __tablename__= "members"

    member_id = Column(Integer, primary_key= True, index= True)
    name = Column(String(50),nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(Integer, nullable=False)
    membership_date = Column(date, nullable=False)
    status = Column(String, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer,ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer,ForeignKey=("member.member_id"), nullable=False)
    issue_date = Column(date, nullable=False)
    due_date = Column(date, nullable=False)
    return_date = Column(date, nullable=False)
    status = Column(String, nullable=False)

app = FastAPI()
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
