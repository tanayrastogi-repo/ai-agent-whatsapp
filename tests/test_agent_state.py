"""Tests for the agent state schema and routing logic."""


from src.agent.state import AgentState, Intent


def test_agent_state_has_required_fields():
    """Test that AgentState has all required fields."""
    state: AgentState = {
        "messages": [],
        "intent": None,
        "tool_result": None,
        "response": None,
    }

    assert "messages" in state
    assert "intent" in state
    assert "tool_result" in state
    assert "response" in state


def test_intent_enum_values():
    """Test that Intent enum has expected values."""
    assert Intent.CREATE_TASK.value == "create_task"
    assert Intent.QUERY_TASKS.value == "query_tasks"
    assert Intent.CLARIFY.value == "clarify"
    assert Intent.UNKNOWN.value == "unknown"


def test_state_update_with_tool_result():
    """Test updating state with tool result."""
    state: AgentState = {
        "messages": [],
        "intent": Intent.CREATE_TASK,
        "tool_result": None,
        "response": None,
    }

    new_state = state.copy()
    new_state["tool_result"] = {"status": "success", "task_id": "123"}

    assert new_state["tool_result"]["status"] == "success"
    assert new_state["tool_result"]["task_id"] == "123"
