# Import OS module to read DATABASE_URL environment variable
import os
# Import SQLAlchemy database engine and session maker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection string default fallback to SQLite for local development or testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine establishing connection to user_db
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create SessionLocal factory class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for user-service models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency delivering database session per HTTP request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
