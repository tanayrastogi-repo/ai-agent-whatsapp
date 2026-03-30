"""LangGraph agent for task management via WhatsApp."""

import re
from datetime import datetime, timedelta
from typing import Any

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from src.agent.state import AgentState, Intent
from src.agent.tools import create_task, get_tasks
from src.agent.router import route_intent

llm = ChatOllama(
    model="llama3.1",
    temperature=0,
)

tools = [create_task, get_tasks]
llm_with_tools = llm.bind_tools(tools)


def router_node(state: AgentState) -> AgentState:
    """Classify user intent using keyword-based routing.

    Args:
        state: Current agent state with messages.

    Returns:
        Updated state with classified intent.
    """
    intent = route_intent(state["messages"])
    return {"intent": intent}


def create_task_node(state: AgentState) -> AgentState:
    """Handle task creation requests.

    Extracts task details from the message and creates a task.

    Args:
        state: Current agent state with messages.

    Returns:
        Updated state with tool_result.
    """
    from langchain_core.messages import HumanMessage

    human_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not human_messages:
        return {
            "tool_result": {
                "status": "error",
                "message": "No message found to parse",
            }
        }

    last_message = human_messages[-1]
    message = str(last_message.content).lower()

    parsed = _parse_create_task_message(message)

    if not parsed["assignee"] or not parsed["description"] or not parsed["deadline"]:
        return {
            "tool_result": {
                "status": "error",
                "message": "Could not extract all required fields from the message. "
                "Please provide: assignee, task description, and deadline.",
            }
        }

    result = create_task.invoke(
        {
            "assignee": parsed["assignee"],
            "description": parsed["description"],
            "deadline": parsed["deadline"],
        }
    )

    return {"tool_result": result}


def get_tasks_node(state: AgentState) -> AgentState:
    """Handle task query requests.

    Extracts query parameters and fetches matching tasks.

    Args:
        state: Current agent state with messages.

    Returns:
        Updated state with tool_result containing task list.
    """
    from langchain_core.messages import HumanMessage

    human_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not human_messages:
        return {
            "tool_result": {
                "status": "error",
                "message": "No message found to parse",
                "tasks": [],
            }
        }

    last_message = human_messages[-1]
    message = str(last_message.content).lower()

    parsed = _parse_query_task_message(message)
    result = get_tasks.invoke(parsed)

    return {"tool_result": result}


def response_builder_node(state: AgentState) -> AgentState:
    """Generate natural language response based on tool result.

    Args:
        state: Current agent state with tool_result.

    Returns:
        Updated state with final response.
    """
    intent = state.get("intent")
    tool_result = state.get("tool_result")

    if tool_result is None:
        response = "I'm not sure how to help with that. Could you please rephrase your request?"
        return {"response": response}

    if tool_result.get("status") == "error":
        response = (
            f"I encountered an issue: {tool_result.get('message', 'Unknown error')}"
        )
        return {"response": response}

    if intent == Intent.CREATE_TASK:
        response = _format_create_response(tool_result)
    elif intent == Intent.QUERY_TASKS:
        response = _format_query_response(tool_result)
    else:
        response = _format_clarify_response()

    return {"response": response}


def _parse_create_task_message(message: str) -> dict[str, Any]:
    """Parse create task message to extract assignee, description, deadline.

    This is a simplified parser. In production, you might use the LLM
    or a more sophisticated NLP approach.

    Args:
        message: The user's message content.

    Returns:
        Dictionary with assignee, description, and deadline.
    """
    import re
    from datetime import datetime

    assignee = None
    description = None
    deadline = None

    assign_patterns = [
        r"(?:ask|tell|assign)\s+(\w+)",
        r"(\w+)\s+(?:to|should|must)",
    ]
    for pattern in assign_patterns:
        match = re.search(pattern, message)
        if match:
            assignee = match.group(1).title()
            if assignee.lower() not in ["i", "you", "me", "we", "they"]:
                break

    desc_patterns = [
        r"(?:to|please)\s+(.+?)\s+(?:by|before|until|due)",
        r"(.+?)\s+(?:by|before|until|due)",
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, message)
        if match:
            description = match.group(1).strip()
            break

    if not description:
        words = message.split()
        stop_words = {
            "can",
            "you",
            "ask",
            "tell",
            "assign",
            "to",
            "please",
            "the",
            "a",
            "an",
        }
        description = " ".join(w for w in words if w.lower() not in stop_words)[:200]

    deadline_patterns = [
        (r"by\s+(\w+)", _parse_day_of_week),
        (r"by\s+tomorrow", lambda _: datetime.now() + timedelta(days=1)),
        (r"by\s+next\s+week", lambda _: datetime.now() + timedelta(weeks=1)),
        (r"by\s+(\d{1,2})[/\-](\d{1,2})", _parse_mdy_date),
    ]

    for pattern, parser in deadline_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            try:
                deadline = parser(match)
                if deadline:
                    deadline = deadline.replace(
                        hour=17, minute=0, second=0, microsecond=0
                    )
                    break
            except (ValueError, IndexError):
                continue

    if not deadline:
        deadline = datetime.now() + timedelta(days=7)

    return {
        "assignee": assignee,
        "description": description,
        "deadline": deadline,
    }


def _parse_day_of_week(match: re.Match) -> datetime | None:
    """Parse day of week to datetime."""
    from datetime import datetime

    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    day_name = match.group(1).lower()
    if day_name not in days:
        return None

    today = datetime.now()
    target_day = days[day_name]
    days_ahead = (target_day - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def _parse_mdy_date(match: re.Match) -> datetime | None:
    """Parse MM/DD or MM-DD date format."""
    from datetime import datetime

    month, day = int(match.group(1)), int(match.group(2))
    year = datetime.now().year
    return datetime(year, month, day)


def _parse_query_task_message(message: str) -> dict[str, Any]:
    """Parse query message to extract filters."""
    import re
    from datetime import datetime

    result = {}

    assignee_match = re.search(
        r"(?:for|to|assigned to|belongs to)\s+(\w+)", message, re.IGNORECASE
    )
    if assignee_match:
        result["assignee"] = assignee_match.group(1).title()

    if "tomorrow" in message.lower():
        tomorrow = datetime.now() + timedelta(days=1)
        result["deadline_before"] = tomorrow.replace(hour=23, minute=59, second=59)

    day_match = re.search(r"by\s+(\w+)", message, re.IGNORECASE)
    if day_match:
        day_name = day_match.group(1).lower()
        days = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        if day_name in days:
            today = datetime.now()
            target_day = days[day_name]
            days_ahead = (target_day - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target_date = today + timedelta(days=days_ahead)
            result["deadline_before"] = target_date.replace(
                hour=23, minute=59, second=59
            )

    return result


def _format_create_response(tool_result: dict[str, Any]) -> str:
    """Format task creation result as natural language."""
    if tool_result.get("status") != "success":
        return f"I had trouble creating the task: {tool_result.get('message', 'Unknown error')}"

    return (
        f"Done! I've created a task for {tool_result.get('assignee')}: "
        f"'{tool_result.get('description')}' due {tool_result.get('deadline')}."
    )


def _format_query_response(tool_result: dict[str, Any]) -> str:
    """Format task query result as natural language."""
    if tool_result.get("status") != "success":
        return (
            f"I couldn't fetch the tasks: {tool_result.get('message', 'Unknown error')}"
        )

    tasks = tool_result.get("tasks", [])
    count = tool_result.get("count", 0)

    if count == 0:
        return "I couldn't find any tasks matching your query."

    if count == 1:
        task = tasks[0]
        return (
            f"Found 1 task for {task['assignee']}: "
            f"'{task['description']}' due {task['deadline']}"
        )

    response_lines = [f"Found {count} tasks:"]
    for i, task in enumerate(tasks, 1):
        status = "✓" if task.get("completed") else "○"
        response_lines.append(
            f"{i}. {status} {task['description']} - {task['assignee']} (due {task['deadline']})"
        )

    return "\n".join(response_lines)


def _format_clarify_response() -> str:
    """Format clarification request."""
    return (
        "I'm a task management assistant. You can:\n\n"
        "• Create tasks: 'Ask John to finish the report by Friday'\n"
        "• Query tasks: 'How many tasks does Alice have due next week?'\n\n"
        "What would you like to do?"
    )


def _route_based_on_intent(state: AgentState) -> str:
    """Route to the appropriate node based on classified intent.

    Args:
        state: Current agent state.

    Returns:
        Node name to route to next.
    """
    intent = state.get("intent", Intent.UNKNOWN)

    if intent == Intent.CREATE_TASK:
        return "create_task_node"
    elif intent == Intent.QUERY_TASKS:
        return "get_tasks_node"
    elif intent == Intent.CLARIFY:
        return "response_builder"
    else:
        return "response_builder"


workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("create_task_node", create_task_node)
workflow.add_node("get_tasks_node", get_tasks_node)
workflow.add_node("response_builder", response_builder_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    _route_based_on_intent,
    {
        "create_task_node": "create_task_node",
        "get_tasks_node": "get_tasks_node",
        "response_builder": "response_builder",
    },
)

workflow.add_edge("create_task_node", "response_builder")
workflow.add_edge("get_tasks_node", "response_builder")
workflow.add_edge("response_builder", END)

app = workflow.compile()
