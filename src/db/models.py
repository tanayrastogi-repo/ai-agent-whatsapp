"""SQLAlchemy database models for the WhatsApp Task Agent."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Inherits from DeclarativeBase which provides the machinery for
    mapping Python classes to database tables. All model classes
    in the application should inherit from this Base class.
    """


class Task(Base):
    """Task model representing a task in the database.

    Attributes:
        id: Unique identifier (UUID string)
        assignee: Person responsible for the task
        description: What needs to be done
        deadline: When the task should be completed
        created_at: When the task was created in the database
        completed: Whether the task has been marked as done
    """

    __tablename__ = "tasks"

    # Primary key with auto-generated UUID
    # String(36) accommodates standard UUID format (e.g., "123e4567-e89b-12d3-a456-426614174000")
    # default=lambda: str(uuid4()) generates a new UUID when a Task is created
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Who is assigned to this task (required field)
    assignee: Mapped[str] = mapped_column(String(255), nullable=False)

    # Task description/details (required field, max 1000 chars)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    # When the task is due (required field)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Automatically set to current time when task is created
    # server_default=func.now() sets this at the database level,
    # not in Python - ensures consistent timestamps regardless of app server timezone
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Whether the task has been completed (defaults to False)
    completed: Mapped[bool] = mapped_column(default=False)

    def to_dict(self) -> dict:
        """Convert task to dictionary representation.

        Useful for serializing tasks to JSON for API responses.

        Returns:
            dict: Task data with ISO-formatted datetime strings
        """
        return {
            "id": self.id,
            "assignee": self.assignee,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed": self.completed,
        }
