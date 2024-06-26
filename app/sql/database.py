import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

engine = create_engine(
    os.getenv("SQLALCHEMY_DATABASE_URL"), connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Create a new database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
