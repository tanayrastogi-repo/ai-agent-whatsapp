"""Tests for agent tools (create_task and get_tasks)."""

import pytest
from datetime import datetime

from src.db.models import Task


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "assignee": "John Doe",
        "description": "Complete the CASA project report for Q2.",
        "deadline": datetime(2026, 4, 15, 17, 0),
    }


@pytest.fixture
def mock_db_session(db_session, monkeypatch):
    """Patch the tools to use the test database session."""
    from src.db import database

    monkeypatch.setattr(database, "SessionLocal", lambda: db_session)
    return db_session


def test_create_task_with_valid_data(mock_db_session, sample_task_data):
    """Test creating a task with valid data."""
    from src.agent.tools import create_task

    result = create_task.invoke(
        {
            "assignee": sample_task_data["assignee"],
            "description": sample_task_data["description"],
            "deadline": sample_task_data["deadline"],
        }
    )

    assert result["status"] == "success"
    assert result["assignee"] == sample_task_data["assignee"]
    assert result["description"] == sample_task_data["description"]
    assert result["id"] is not None

    tasks = mock_db_session.query(Task).all()
    assert len(tasks) == 1
    assert tasks[0].assignee == sample_task_data["assignee"]


def test_create_task_stores_in_database(mock_db_session, sample_task_data):
    """Test that created task is persisted in database."""
    from src.agent.tools import create_task

    result = create_task.invoke(
        {
            "assignee": sample_task_data["assignee"],
            "description": sample_task_data["description"],
            "deadline": sample_task_data["deadline"],
        }
    )

    task = mock_db_session.query(Task).filter_by(id=result["id"]).first()
    assert task is not None
    assert task.assignee == sample_task_data["assignee"]
    assert task.description == sample_task_data["description"]


def test_get_tasks_returns_list(mock_db_session):
    """Test that get_tasks returns a list of tasks."""
    from src.agent.tools import create_task, get_tasks

    create_task.invoke(
        {
            "assignee": "Alice",
            "description": "Finish the code review for the new feature.",
            "deadline": datetime(2026, 4, 1),
        }
    )
    create_task.invoke(
        {
            "assignee": "Alice",
            "description": "Order the new laptops for the team.",
            "deadline": datetime(2026, 4, 2),
        }
    )

    result = get_tasks.invoke({"assignee": "Alice"})

    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["tasks"]) == 2


def test_get_tasks_filter_by_assignee(mock_db_session):
    """Test filtering tasks by assignee."""
    from src.agent.tools import create_task, get_tasks

    create_task.invoke(
        {
            "assignee": "Bob",
            "description": "Do the monthly financial report for the board meeting.",
            "deadline": datetime(2026, 4, 11),
        }
    )
    create_task.invoke(
        {
            "assignee": "Bob",
            "description": "Finish the quarterly budget review for the finance team.",
            "deadline": datetime(2026, 4, 2),
        }
    )

    result = get_tasks.invoke({"assignee": "Bob"})

    assert result["count"] == 2
    assert result["tasks"][0]["assignee"] == "Bob"


def test_get_tasks_filter_by_deadline(mock_db_session):
    """Test filtering tasks by deadline."""
    from src.agent.tools import create_task, get_tasks

    create_task.invoke(
        {
            "assignee": "Test",
            "description": "Early task",
            "deadline": datetime(2026, 4, 1),
        }
    )
    create_task.invoke(
        {
            "assignee": "Test",
            "description": "Late task",
            "deadline": datetime(2026, 4, 15),
        }
    )

    result = get_tasks.invoke(
        {"assignee": "Test", "deadline_before": datetime(2026, 4, 10)}
    )

    assert result["count"] == 1
    assert "April 01" in result["tasks"][0]["deadline"]


def test_get_tasks_empty_result(mock_db_session):
    """Test get_tasks returns empty list when no matches."""
    from src.agent.tools import get_tasks

    result = get_tasks.invoke({"assignee": "Nobody"})

    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["tasks"] == []
