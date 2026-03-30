"""Test script to verify LangSmith tracing with LangGraph.

Run this script to generate traces in LangSmith:
    PYTHONPATH=. uv run python tests/test_langsmith_trace.py

Then view traces at: https://smith.langchain.com
"""

from langchain_core.messages import HumanMessage
from langchain_core.tracers import LangChainTracer
from dotenv import load_dotenv

load_dotenv()

from src.agent.graph import app  # noqa: E402


def get_tracer():
    """Get LangChain tracer configured for LangSmith."""
    return LangChainTracer(
        project_name="whatsapp-task-agent",
    )


def test_create_task_flow():
    """Test the create task flow which triggers tool calls."""
    print("\n", "-" * 20)
    print("Testing create task flow...")
    print("-" * 20)

    result = app.invoke(
        {"messages": [HumanMessage(content="Ask John to finish the report by Friday")]},
        config={"callbacks": [get_tracer()]},
    )

    print(f"Response: {result.get('response')}")
    print(f"Intent: {result.get('intent')}")
    print(f"Tool result: {result.get('tool_result')}")
    assert result.get("response") is not None


def test_query_tasks_flow():
    """Test the query tasks flow which triggers tool calls."""
    print("\n", "-" * 20)
    print("Testing query tasks flow...")
    print("-" * 20)

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content="How many tasks does Alice have by Friday?")
            ]
        },
        config={"callbacks": [get_tracer()]},
    )

    print(f"Response: {result.get('response')}")
    print(f"Intent: {result.get('intent')}")
    print(f"Tool result: {result.get('tool_result')}")
    assert result.get("response") is not None


def test_clarify_flow():
    """Test the clarify flow (no tool calls)."""
    print("\n", "-" * 20)
    print("Testing clarify flow...")
    print("-" * 20)

    result = app.invoke(
        {"messages": [HumanMessage(content="Hello!")]},
        config={"callbacks": [get_tracer()]},
    )

    print(f"Response: {result.get('response')}")
    assert result.get("response") is not None


if __name__ == "__main__":
    print("=" * 60)
    print("LangSmith Tracing Test")
    print("=" * 60)

    test_create_task_flow()
    test_query_tasks_flow()
    test_clarify_flow()

    print("\n" + "=" * 60)
    print("Check https://smith.langchain.com for traces")
    print("=" * 60)
    print("LangSmith Tracing Test")
    print("=" * 60)
