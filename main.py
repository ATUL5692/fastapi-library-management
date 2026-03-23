from fastapi import FastAPI
from database import engine
import models

from routers import books, members, transactions, analytics

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(members.router, prefix="/member", tags=["Member"]) 
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])