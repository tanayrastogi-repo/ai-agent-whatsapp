# Agent Guidelines for ai-agent

## Project Overview
WhatsApp AI Agent using LangChain DeepAgent with FastAPI webhooks, SQLite database, and Twilio WhatsApp integration.

### Capabilities
1. **Task Management** - Create and query tasks in SQLite database
2. **Web Search** - Search the web for current information (DuckDuckGo)
3. **Data Analysis** - Execute Python code for calculations and visualizations (Daytona sandbox)

---

## Build, Lint, and Test Commands

### Package Management (uv)
```bash
# Install dependencies
uv sync

# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Remove a dependency
uv remove <package>

# Update lock file
uv lock

# Run scripts with dependencies
uv run python script.py
```

### Running the Application
```bash
# Start the FastAPI server
uv run uvicorn main:app --reload --port 8000

# Health check
curl http://localhost:8000/health
```

### Testing Commands
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_webhook.py

# Run a single test function
uv run pytest tests/test_webhook.py::test_health_check

# Run tests matching a pattern
uv run pytest -k "webhook"

# Run tests with verbose output
uv run pytest -v

# Run sync tests only
uv run pytest -v -m "not asyncio"

# Run async tests only
uv run pytest tests/test_webhook_async.py -v

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Linting and Type Checking
```bash
# Run ruff linter with auto-fix
uv run ruff check . --fix

# Run mypy type checker
uv run mypy .

# Run all checks (lint + type check)
uv run ruff check . && uv run mypy .
```

---

## Code Style Guidelines

### Python Version
- **Required:** Python 3.11+
- Specify in `.python-version`

### Import Conventions
```python
# Standard library imports (alphabetical)
import json
import os
from datetime import datetime
from typing import Optional

# Third-party imports (alphabetical)
from fastapi import FastAPI, HTTPException
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

# Local imports (alphabetical, use absolute imports from src/)
from src.agent.graph import app
from src.db.models import Task
```

### Formatting
- **Line length:** 88 characters (ruff/black default)
- **Indentation:** 4 spaces (no tabs)
- **Use Black** for automatic formatting
- **Trailing commas** for multi-line structures
- **Run ruff with --fix** before committing to auto-fix issues

### Naming Conventions
```
Modules:         snake_case (e.g., task_manager.py)
Classes:         PascalCase (e.g., TaskManager, BaseModel)
Functions:       snake_case (e.g., get_tasks, create_task)
Variables:       snake_case (e.g., user_id, task_list)
Constants:       UPPER_SNAKE_CASE (e.g., MAX_RETRIES, API_TIMEOUT)
Type Variables:  PascalCase (e.g., T, TaskType)
Private methods: _leading_underscore (e.g., _internal_method)
```

### Type Annotations
```python
# Function signatures must have type hints
def get_tasks(user_id: str, deadline: Optional[datetime] = None) -> list[Task]:
    ...

# Use typing module for complex types
from typing import Optional, Union, Callable
from collections.abc import AsyncIterator

# Pydantic models for data validation
class TaskCreate(BaseModel):
    assignee: str
    description: str
    deadline: Optional[datetime] = None

# Suppress type errors for external libraries without stubs
from twilio.twiml import MessagingResponse  # type: ignore[import-untyped]
```

### Error Handling
```python
# Use FastAPI's HTTPException for API errors
from fastapi import HTTPException

def get_task(task_id: str) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Custom exceptions for business logic
class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class TaskParseError(AgentError):
    """Raised when task parsing fails."""
    pass
```

### Docstrings
```python
def create_task(assignee: str, description: str, deadline: datetime) -> Task:
    """Create a new task in the database.

    Args:
        assignee: The person responsible for the task.
        description: The task description.
        deadline: When the task should be completed.

    Returns:
        The created Task object.

    Raises:
        ValueError: If assignee or description is empty.
    """
    ...
```

### Async Code
```python
# Use async/await for FastAPI route handlers
async def webhook_endpoint(Body: str = Form(None)) -> Response:
    result = await process_message(Body)
    return Response(content=str(result), media_type="text/xml")

# Test async code with pytest-asyncio and httpx
import pytest
from httpx import ASGITransport, AsyncClient

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_webhook(async_client):
    response = await async_client.post("/webhook", data={"Body": "Hello!"})
    assert response.status_code == 200
```

---

## Project Structure
```
ai-agent/
├── main.py                  # FastAPI webhook server entry point
├── pyproject.toml           # Project configuration
├── .python-version          # Python version specification
├── .env                     # Environment variables (gitignore)
├── src/                     # Source code
│   ├── __init__.py
│   ├── agent/               # LangChain DeepAgent logic
│   │   ├── __init__.py
│   │   ├── graph.py         # DeepAgent creation (create_deep_agent)
│   │   ├── graph_deepagent.py  # Backup of current implementation
│   │   ├── router.py        # DEPRECATED - Intent classification (retained for reference)
│   │   ├── state.py         # AgentState TypedDict, Intent enum
│   │   ├── tools.py         # Tools: create_task, get_tasks, web_search, data_analysis
│   │   └── langsmith_config.py
│   └── db/                  # Database layer
│       ├── __init__.py
│       ├── models.py         # SQLAlchemy Task model
│       └── database.py       # Engine, session, get_db
└── tests/                   # Test files
    ├── __init__.py
    ├── conftest.py          # pytest fixtures (db_session)
    ├── test_*.py            # Test modules
    └── test_webhook_async.py # Async tests with httpx
```

---

## Dependencies

### Core (add via `uv add`)
- **deepagents** - DeepAgent framework for planning and tool calling
- **langchain**, **langgraph** - Agent framework
- **langchain-ollama** - Ollama LLM integration
- **langchain-community** - Community tools (DuckDuckGo)
- **langchain-daytona-data-analysis** - Data analysis sandbox
- **sqlalchemy** - Database ORM
- **fastapi**, **uvicorn** - Web server
- **python-multipart** - Form data parsing for FastAPI
- **pydantic** - Data validation
- **twilio** - WhatsApp integration
- **python-dotenv** - Environment variable loading
- **ddgs** - DuckDuckGo search

### Dev (add via `uv add --dev`)
- **pytest**, **pytest-asyncio** - Testing with async support
- **httpx** - Async HTTP client for tests
- **ruff**, **mypy** - Linting/type checking

---

## Environment Variables
Create a `.env` file (never commit):
```
# OLLAMA CONFIGURATION
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# OLLAMA CLOUD (primary model for DeepAgent)
OLLAMA_API_KEY=your_ollama_cloud_key

# DAYTONA (data analysis sandbox)
DAYTONA_API_KEY=your_daytona_key

# DATABASE
DATABASE_URL=sqlite:///./tasks.db

# TWILIO
TWILIO_AUTH_TOKEN=xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_PHONE_NUMBER=xxx

# LANGSMITH
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=xxx
LANGSMITH_PROJECT=whatsapp-task-agent
```

---

## Models

The agent uses model fallback:
- **Primary**: `qwen3.5:397b-cloud` (Ollama Cloud) - requires `OLLAMA_API_KEY`
- **Fallback**: `llama3.2:3b` (local) - used when cloud is unavailable

---

## Key Patterns

### DeepAgent Creation
```python
from deepagents import create_deep_agent
from src.agent.tools import create_task, get_tasks, web_search, data_analysis

TOOLS = [create_task, get_tasks, web_search, data_analysis]

agent = create_deep_agent(
    model=ChatOllama(model="qwen3.5:397b-cloud"),
    tools=TOOLS,
    system_prompt="You are a helpful WhatsApp assistant...",
)
```

### DeepAgent Invocation
```python
from langchain_core.messages import HumanMessage
from langchain_core.tracers import LangChainTracer

tracer = LangChainTracer(project_name="whatsapp-task-agent")
result = app.invoke(
    {"messages": [HumanMessage(content=message)]},
    config={"callbacks": [tracer]},
)
response = result.get("messages", [])[-1].content
```

### FastAPI TwiML Response
```python
from fastapi import Response
from twilio.twiml.messaging_response import MessagingResponse

twiml = MessagingResponse()
twiml.message("Reply text")
return Response(content=str(twiml), media_type="text/xml")
```

### Database Session Pattern
```python
from src.db.database import SessionLocal, get_db

# In FastAPI route
db = next(get_db())
try:
    task = db.query(Task).all()
finally:
    db.close()
```

---

## Tools

The DeepAgent has access to four tools:

| Tool | Function |
|------|----------|
| `create_task` | Creates a task in the SQLite database |
| `get_tasks` | Queries tasks with optional filters |
| `web_search` | Searches the web using DuckDuckGo |
| `data_analysis` | Executes Python code in Daytona sandbox |

---

## Verification Checklist Before Committing
- [ ] All tests pass: `uv run pytest -v`
- [ ] No lint errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] Update AGENTS.md if project structure changes
