from fastapi import FastAPI
from database import engine
import models

from routers import books, members, transactions, analytics

app = FastAPI()

# create tables
models.Base.metadata.create_all(bind=engine)

# include routers
app.include_router(books.router)
app.include_router(members.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
