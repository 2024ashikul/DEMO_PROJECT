# Import OS module to retrieve DATABASE_URL from environment variables
import os
# Import SQLAlchemy create_engine to manage database connection pool
from sqlalchemy import create_engine
# Import sessionmaker to instantiate database session objects
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection string default fallback to SQLite for local development or testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")

# SQLite requires connect_args check_same_thread=False for multi-threaded FastAPI requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine establishing connection to database
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create a database session factory class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for SQLAlchemy DB Table models to inherit from
Base = declarative_base()

def get_db():
    """
    FastAPI dependency function providing a transactional database session per HTTP request.
    Yields session and guarantees cleanup/close on request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
