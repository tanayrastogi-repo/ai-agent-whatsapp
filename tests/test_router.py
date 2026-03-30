"""Tests for the router function."""

from src.agent.router import route_intent
from src.agent.state import Intent


class TestRouteIntent:
    """Tests for the route_intent function."""

    def test_detects_create_task_intent(self):
        """Test that create task patterns are correctly identified."""
        messages = [
            {
                "type": "human",
                "content": "Hey, can you ask Joe to finish the report by Friday?",
            }
        ]
        intent = route_intent(messages)
        assert intent == Intent.CREATE_TASK

    def test_detects_create_task_with_assignee(self):
        """Test create task with explicit assignee."""
        messages = [
            {
                "type": "human",
                "content": "Please assign this task to Sarah to complete the documentation by Monday",
            }
        ]
        intent = route_intent(messages)
        assert intent == Intent.CREATE_TASK

    def test_detects_query_intent(self):
        """Test that query patterns are correctly identified."""
        messages = [
            {
                "type": "human",
                "content": "How many tasks does John have to do by next week?",
            }
        ]
        intent = route_intent(messages)
        assert intent == Intent.QUERY_TASKS

    def test_detects_query_intent_what_tasks(self):
        """Test query with 'what tasks' pattern."""
        messages = [{"type": "human", "content": "What tasks are assigned to Alice?"}]
        intent = route_intent(messages)
        assert intent == Intent.QUERY_TASKS

    def test_detects_clarify_intent(self):
        """Test that unclear messages get clarified."""
        messages = [{"type": "human", "content": "Hello there!"}]
        intent = route_intent(messages)
        assert intent == Intent.CLARIFY

    def test_detects_clarify_for_vague_requests(self):
        """Test that vague requests need clarification."""
        messages = [{"type": "human", "content": "Can you help me?"}]
        intent = route_intent(messages)
        assert intent == Intent.CLARIFY

    def test_empty_messages_returns_unknown(self):
        """Test that empty messages return unknown intent."""
        messages = []
        intent = route_intent(messages)
        assert intent == Intent.UNKNOWN

    def test_multiple_human_messages_uses_last(self):
        """Test that the last human message is used for routing."""
        messages = [
            {"type": "human", "content": "Hello"},
            {"type": "ai", "content": "Hi, how can I help?"},
            {"type": "human", "content": "Show me John's tasks due tomorrow"},
        ]
        intent = route_intent(messages)
        assert intent == Intent.QUERY_TASKS
