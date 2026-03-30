"""Database configuration and session management for the WhatsApp Task Agent.

This module provides:
- SQLAlchemy engine and session factory configuration
- Database table creation utilities
- FastAPI dependency injection for database sessions
"""

from collections.abc import Generator
from os import getenv
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables from .env file into the process
load_dotenv()

from src.db.models import Base  # noqa: E402

# Get DATABASE_URL from environment, with fallback default for local development
# This allows the database location to be configured via environment variables
DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Create SQLAlchemy engine with SQLite-specific configuration
# check_same_thread=False: SQLite connections can be shared across threads.
# Required because FastAPI may handle requests in different threads than the
# one where the engine was created.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory for creating database sessions
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Session won't auto-flush changes before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all database tables defined in SQLAlchemy models.

    Uses SQLAlchemy's metadata system to create tables that don't exist yet.
    Safe to call multiple times - only creates tables that don't exist.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session.

    Yields a database session that will be automatically closed when the
    request handler completes. Ensures proper cleanup even if an exception
    occurs during the request.

    Usage:
        @app.get("/tasks")
        def get_tasks(db: DbSession):
            return db.query(Task).all()

    Yields:
        Session: A SQLAlchemy session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for FastAPI dependency injection
# Allows using `db: DbSession` as a route parameter instead of
# `db: Session = Depends(get_db)`
DbSession = Annotated[Session, Depends(get_db)]
