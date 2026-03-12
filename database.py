from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine


DATABASE_URL = "mysql+pymysql://root:M%40ngo112@localhost/library_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
