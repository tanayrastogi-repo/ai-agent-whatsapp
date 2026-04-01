"""Tests for the full agent graph."""


class TestAgentGraph:
    """Tests for the compiled agent graph."""

    def test_agent_graph_compiles(self):
        """Test that the agent graph compiles without errors."""
        from src.agent.graph import app

        assert app is not None
        assert hasattr(app, "invoke")

    def test_agent_has_invoke_method(self):
        """Test that the agent has an invoke method."""
        from src.agent.graph import app

        assert callable(app.invoke)


class TestAgentInvocation:
    """Tests for invoking the agent."""

    def test_agent_returns_response(self):
        """Test that agent returns a response structure."""
        from src.agent.graph import app
        from langchain_core.messages import HumanMessage

        result = app.invoke(
            {
                "messages": [HumanMessage(content="Hello there!")],
                "intent": None,
                "tool_result": None,
                "response": None,
            }
        )

        messages = result.get("messages", [])
        assert len(messages) >= 2
        response_msg = messages[-1]
        assert response_msg.type == "ai"
        assert response_msg.content

    def test_agent_handles_clarify_message(self):
        """Test agent handles greeting/clarification."""
        from src.agent.graph import app
        from langchain_core.messages import HumanMessage

        result = app.invoke(
            {
                "messages": [HumanMessage(content="Hello!")],
                "intent": None,
                "tool_result": None,
                "response": None,
            }
        )

        messages = result.get("messages", [])
        assert len(messages) >= 2
        response_msg = messages[-1]
        assert response_msg.type == "ai"
        assert response_msg.content
