from pydantic import BaseModel
from datetime import date

# Validation for Books
class BookCreate(BaseModel):
    title:str
    author:str
    isbn:int
    category:str
    total_copies:int
    available_copies:int
    shelf_location:str
class BookResponse(BaseModel):
    id:int
    title:str
    author:str
    isbn:int
    category:str
    total_copies:int
    available_copies:int
    shelf_location:str

    class Config:
        from_arrributes=True





# Validation for Members
class MembersCreate(BaseModel):
    name:str
    email:str
    phone:int
    membership_date:date
    status:str

class MembersResponse(BaseModel):
    member_id:int
    name:str
    email:str
    phone:int
    membership_date:date
    status:str

    class Config:
        from_attributes=True




# Validation for Transactions data

class TransactionsCreate(BaseModel):
    member_id:int
    issue_date:date
    due_date:date
    return_date:date
    status:str

class TransactionsResponse(BaseModel):
    transaction_id:int
    book_id:int
    member_id:int
    issue_date:date
    due_date:date
    return_date:date
    status:str
    class Config:
        from_attributes=True
