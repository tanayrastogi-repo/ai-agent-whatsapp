"""Tools for the task management agent.

This module provides LangChain tools for creating and querying tasks
in the SQLite database.
"""

from datetime import datetime
from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.db.models import Task


@tool
def create_task(
    assignee: str,
    description: str,
    deadline: datetime,
) -> dict[str, Any]:
    """Create a new task in the database.

    Args:
        assignee: The person responsible for the task.
        description: The task description/details.
        deadline: When the task should be completed.

    Returns:
        A dictionary with status, task details, and message.
    """
    from src.db.database import SessionLocal

    db: Session = SessionLocal()
    try:
        task = Task(
            assignee=assignee,
            description=description,
            deadline=deadline,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        deadline_str = task.deadline.strftime("%B %d, %Y at %I:%M %p")
        return {
            "status": "success",
            "id": task.id,
            "assignee": task.assignee,
            "description": task.description,
            "deadline": deadline_str,
            "message": f"Task created: '{description}' assigned to {assignee}, due {deadline_str}",
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}",
        }
    finally:
        db.close()


@tool
def get_tasks(
    assignee: str | None = None,
    deadline_before: datetime | None = None,
    deadline_after: datetime | None = None,
) -> dict[str, Any]:
    """Query tasks from the database with optional filters.

    Args:
        assignee: Filter tasks by assignee name.
        deadline_before: Filter tasks with deadline before this date.
        deadline_after: Filter tasks with deadline after this date.

    Returns:
        A dictionary with status, count, and list of tasks.
    """
    from src.db.database import SessionLocal

    db: Session = SessionLocal()
    try:
        query = db.query(Task)

        if assignee:
            query = query.filter(Task.assignee.ilike(f"%{assignee}%"))

        if deadline_before:
            query = query.filter(Task.deadline <= deadline_before)

        if deadline_after:
            query = query.filter(Task.deadline >= deadline_after)

        query = query.order_by(Task.deadline.asc())
        tasks = query.all()

        task_list = [
            {
                "id": task.id,
                "assignee": task.assignee,
                "description": task.description,
                "deadline": task.deadline.strftime("%B %d, %Y"),
                "completed": task.completed,
            }
            for task in tasks
        ]

        return {
            "status": "success",
            "count": len(task_list),
            "tasks": task_list,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to query tasks: {str(e)}",
            "tasks": [],
        }
    finally:
        db.close()
