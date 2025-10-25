"""Database configuration and session management."""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Check if we're running in test mode
TEST_MODE = os.getenv("PROVISIONR_TEST_MODE", "false").lower() == "true"

# Use in-memory database for tests, SQLite file for production
if TEST_MODE:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    connect_args = {"check_same_thread": False}
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./provisionr.db"
    connect_args = {"check_same_thread": False}

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    # Enable connection pooling for better thread safety
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.

    Use with FastAPI Depends() to inject database session into routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
