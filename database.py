from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


DATABASE_URL = "mysql+pymysql://root:M%40ngo112@localhost/library"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()