"""Agent state schema and types for LangGraph."""

from enum import Enum
from typing import Annotated, Any

from langgraph.graph import add_messages
from typing_extensions import TypedDict


class Intent(str, Enum):
    """Enumeration of possible agent intents."""

    CREATE_TASK = "create_task"
    QUERY_TASKS = "query_tasks"
    CLARIFY = "clarify"
    UNKNOWN = "unknown"


class AgentState(TypedDict, total=False):
    """State schema for the task management agent.

    Attributes:
        messages: List of conversation messages (HumanMessage, AIMessage, etc.)
        intent: The classified intent of the user's message
        tool_result: Result from tool execution (if any)
        response: Final natural language response to send back
    """

    messages: Annotated[list[Any], add_messages]
    intent: Intent | None
    tool_result: dict[str, Any] | None
    response: str | None
