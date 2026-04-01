import os
import sys
import httpx
from langchain_ollama import ChatOllama
from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, "/home/tanay/projects/ai-agent-whatsapp")
from src.agent.graph import app


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


OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
if not OLLAMA_API_KEY:
    print("❌ OLLAMA_API_KEY not set in environment")
    exit(1)




# # Create the OLLAMA chat model instance
# model = ChatOllama(
#         model="qwen3.5:397b-cloud",
#         base_url="https://ollama.com/",
#         api_key=OLLAMA_API_KEY,
#         temperature=0,
# )

# # Create the DeepAgent with the OLLAMA model and system prompt
# app = create_deep_agent(
#     model=model,
#     system_prompt=SYSTEM_PROMPT,
# )


# Run the agent
result = app.invoke(
    {
        "messages": [HumanMessage(content="Hello there!")],
        "intent": None,
        "tool_result": None,
        "response": None,
    }
)
print("Agent response:")
print(result)
