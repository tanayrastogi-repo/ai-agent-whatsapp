"""Tools for the task management agent.

This module provides LangChain tools for creating and querying tasks
in the SQLite database.
"""

from datetime import datetime
from typing import Any

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from sqlalchemy.orm import Session

from src.db.models import Task


# Daytona tool singleton
_daytona_tool = None


def get_daytona_tool():
    """Get or create DaytonaDataAnalysisTool singleton."""
    global _daytona_tool
    if _daytona_tool is None:
        from langchain_daytona_data_analysis import DaytonaDataAnalysisTool

        _daytona_tool = DaytonaDataAnalysisTool()
    return _daytona_tool


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


@tool
def web_search(query: str) -> str:
    """Search the web for current information.

    Use this tool when users ask about current events, facts,
    or information that requires up-to-date web results.

    Args:
        query: The search query string.

    Returns:
        Search results as a formatted string with snippets.
    """
    search = DuckDuckGoSearchRun()
    return search.invoke(query)


@tool
def data_analysis(code: str) -> str:
    """Execute Python code for data analysis and visualization.

    Use this tool when users ask to:
    - Perform mathematical calculations
    - Analyze data
    - Create charts and visualizations
    - Run Python scripts

    The tool runs in a secure sandboxed environment and can generate
    plots as image artifacts.

    Args:
        code: Python code to execute. Can include:
        - Mathematical expressions
        - Data manipulation (pandas)
        - Visualization (matplotlib, seaborn)
        - File operations

    Returns:
        Execution results including any text output or artifact descriptions.
    """
    tool = get_daytona_tool()
    try:
        result = tool.invoke({"data_analysis_python_code": code})
        return str(result)
    except Exception as e:
        return f"Error executing code: {str(e)}"
