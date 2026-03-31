# # This file is for connecting project to DB

# from sqlalchemy.orm import declarative_base, sessionmaker
# from sqlalchemy import create_engine


# DATABASE_URL = "mysql+pymysql://root:M%40ngo112@localhost/library"

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



# Postgres sql implementation for deployment.

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os

# =========================
# GET ENV DATABASE
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# LOCAL FALLBACK (IMPORTANT)
# =========================
if DATABASE_URL is None or DATABASE_URL == "":
    DATABASE_URL = "mysql+pymysql://root:M%40ngo112@localhost/library"

# =========================
# FIX POSTGRES URL
# =========================
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# =========================
# ENGINE
# =========================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# =========================
# SESSION
# =========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# =========================
# DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()