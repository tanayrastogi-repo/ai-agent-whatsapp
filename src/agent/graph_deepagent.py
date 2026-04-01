"""LangChain DeepAgent for task management via WhatsApp."""
import os
from langchain_ollama import ChatOllama
from deepagents import create_deep_agent
from src.agent.tools import create_task, get_tasks, web_search, data_analysis
from dotenv import load_dotenv
load_dotenv()


TOOLS = [create_task, get_tasks, web_search, data_analysis]


def get_model() -> ChatOllama:
    """Get LLM with cloud fallback to local.

    Tries to use qwen3.5:397b-cloud from Ollama Cloud.
    Falls back to local llama3.2:3b if cloud fails.

    Returns:
        ChatOllama instance configured with appropriate model.
    """
    ollama_api_key = os.environ.get("OLLAMA_API_KEY")

    if ollama_api_key:
        try:
            return ChatOllama(
                model="qwen3.5:397b-cloud",
                api_key=ollama_api_key,  # type: ignore[call-arg]
                temperature=0,
            )
        except Exception as cloud_error:
            print(f"Cloud model failed: {cloud_error}, falling back to local")

    return ChatOllama(
        model="llama3.2:3b",
        temperature=0,
    )


SYSTEM_PROMPT = """You are a helpful WhatsApp assistant that can assist users with various tasks.

You have access to the following tools:
- create_task: Create a new task in the database
- get_tasks: Query existing tasks
- web_search: Search the web for current information
- data_analysis: Execute Python code for calculations and visualizations

## Capabilities:

### Task Management:
- Create tasks: "Ask John to finish the report by Friday"
- Query tasks: "How many tasks does John have?"
- List all tasks: "Show me all tasks"

### Web Search:
- Use for current events, facts, or information that needs live data
- "What's the weather in San Francisco?"
- "Who won the latest football match?"

### Data Analysis:
- Mathematical calculations: "Calculate compound interest for 1000 at 5% for 5 years"
- Data visualization: "Create a bar chart of sales data"
- Python execution: "Generate fibonacci sequence of 10 numbers"

## Guidelines:
1. Choose the appropriate tool based on the user's request
2. If a request is ambiguous, ask for clarification
3. Keep responses concise (under 4096 characters for WhatsApp)
4. Format mathematical results clearly
5. When generating visualizations, describe what was created

Respond helpfully and accurately to user requests."""


def create_whatsapp_agent():
    """Create the WhatsApp DeepAgent.

    Returns:
        Compiled DeepAgent graph.
    """
    model = get_model()

    agent = create_deep_agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


app = create_whatsapp_agent()
