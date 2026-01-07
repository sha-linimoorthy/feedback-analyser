# Database connection & session

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

"""
Sets up the database connection, sessions and ORM base.
Function to get a db session and then initialize the db tables
"""

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping = True,pool_size = 10, max_overflow = 20)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

def get_db():
    "DB session dependency"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    "Initialize db tables"
    from app.models import FeedbackForm, FeedbackResponse, SentimentAnalysis
    Base.metadata.create_all(bind = engine)