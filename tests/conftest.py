"""Pytest configuration and shared fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models import Base


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing.

    This fixture provides a clean, isolated database for each test function.
    The database is created in memory (not persisted to disk) using SQLite's
    special :memory: connection string.

    Key configuration:
    - sqlite:///:memory: - Creates a temporary in-memory database
    - StaticPool - Keeps the same connection throughout the test (required for :memory: with multiple connections)
    - check_same_thread=False - Allows connection sharing across threads

    Yields:
        Session: A SQLAlchemy session connected to the test database
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
