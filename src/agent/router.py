"""Router module for classifying user intent."""

from typing import Any

from src.agent.state import Intent

QUERY_TASK_PATTERNS = [
    "how many",
    "what tasks",
    "show me",
    "list",
    "tasks for",
    "tasks assigned",
    "what is",
    "what are",
    "who has",
    "due by",
    "due before",
    "upcoming",
    "remaining",
]

CREATE_TASK_PATTERNS = [
    "ask",
    "assign",
    "please",
    "create task",
    "add task",
    "tell",
    "remind",
    "need to",
    "should",
    "must",
    "have to",
]

GREETING_PATTERNS = [
    "hello",
    "hi",
    "hey",
    "how are you",
    "good morning",
    "good afternoon",
    "good evening",
]

INTENT_PATTERNS = [
    (QUERY_TASK_PATTERNS, Intent.QUERY_TASKS),
    (CREATE_TASK_PATTERNS, Intent.CREATE_TASK),
    (GREETING_PATTERNS, Intent.CLARIFY),
]


def route_intent(messages: list[Any]) -> Intent:
    """Classify user intent based on the last human message.

    Args:
        messages: List of messages (can be dicts or LangChain message objects).

    Returns:
        Intent: The classified intent (CREATE_TASK, QUERY_TASKS, CLARIFY, or UNKNOWN).
    """
    human_messages = []

    for m in messages:
        if isinstance(m, dict):
            if m.get("type") == "human":
                human_messages.append(m)
        elif hasattr(m, "type") and m.type == "human":
            human_messages.append({"type": "human", "content": m.content})

    if not human_messages:
        return Intent.UNKNOWN

    last_message = human_messages[-1].get("content", "").lower()

    if not last_message:
        return Intent.UNKNOWN

    for patterns, intent in INTENT_PATTERNS:
        if any(pattern in last_message for pattern in patterns):
            return intent

    if "thanks" in last_message or "thank you" in last_message:
        return Intent.CLARIFY

    if "help" in last_message or "what can you" in last_message:
        return Intent.CLARIFY

    return Intent.UNKNOWN
