"""Database tests for the WhatsApp Task Agent."""

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
    # Create all tables defined in models (Task table in this case)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_db_connection(db_session):
    """Test basic database CRUD operations.

    Verifies that:
    1. A Task can be created and saved to the database
    2. The auto-generated UUID id is populated
    3. Tasks can be queried back from the database
    4. The saved data matches what was inserted
    """
    from datetime import datetime

    from src.db.models import Task

    # CREATE: Add a new task to the database
    task = Task(
        assignee="Test User",
        description="Test task",
        deadline=datetime.now(),
    )
    db_session.add(task)  # Stage the object for insertion
    db_session.commit()  # Persist to database (generates id)

    # VERIFY: Check that id was auto-generated
    assert task.id is not None

    # READ: Query all tasks and verify count
    tasks = db_session.query(Task).all()
    assert len(tasks) == 1

    # VERIFY: Check that saved data matches input
    assert tasks[0].assignee == "Test User"
