from fastapi import FastAPI
from database import engine, SessionLocal
import models

from routers import books, transactions, analytics, users, auth
from fastapi.middleware.cors import CORSMiddleware


# =========================
# APP INIT
# =========================
app = FastAPI(title="Online Library API")


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DATABASE INIT
# =========================
models.Base.metadata.create_all(bind=engine)


# =========================
# ⚠️ TEMP CLEANUP (REMOVE AFTER FIRST RUN)
# =========================
@app.on_event("startup")
def clear_users():
    db = SessionLocal()
    try:
        db.query(models.User).delete()
        db.commit()
        print("🔥 USERS TABLE CLEARED")
    finally:
        db.close()


# =========================
# ROUTERS
# =========================
app.include_router(auth.router)  # already has /auth prefix inside
app.include_router(users.router, prefix="/user", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "Library API is running successfully"}