# DeepAgent Implementation Tasks

This document lists the tasks required to convert the WhatsApp Task Management Agent to a LangChain DeepAgent.

---

## Phase 1: Dependencies

### Task 1.1: Install New Packages
- [ ] Run `uv add deepagents ddgs langchain-daytona-data-analysis`
- [ ] Verify packages are installed correctly
- [ ] Run `uv sync` to ensure lock file is updated

### Task 1.2: Update pyproject.toml
- [ ] Verify new dependencies are listed in `pyproject.toml`
- [ ] Run `uv lock` to update lock file

**Verification:**
```bash
uv run python -c "import deepagents; import ddgs; import langchain_daytona_data_analysis; print('All packages imported successfully')"
```

---

## Phase 2: Environment Configuration

### Task 2.1: Update .env File
- [ ] Add `DAYTONA_API_KEY=your_daytona_api_key_here` to `.env`
- [ ] Add `OLLAMA_API_KEY=your_ollama_cloud_api_key_here` to `.env`
- [ ] Add `OLLAMA_BASE_URL=http://localhost:11434` to `.env`
- [ ] Verify all existing variables are still present
- [ ] Replace placeholder values with actual API keys

**Note:** Get `DAYTONA_API_KEY` from https://app.daytona.io/dashboard/keys
**Note:** Get `OLLAMA_API_KEY` from https://ollama.com/cloud

**Verification:**
```bash
source .env && echo "DAYTONA_API_KEY set: $([ -n "$DAYTONA_API_KEY" ] && echo 'yes' || echo 'no')"
source .env && echo "OLLAMA_API_KEY set: $([ -n "$OLLAMA_API_KEY" ] && echo 'yes' || echo 'no')"
```

---

## Phase 3: Tool Definitions

### Task 3.1: Add Daytona Tool Singleton
- [ ] Import `DaytonaDataAnalysisTool` from `langchain_daytona_data_analysis`
- [ ] Create `get_daytona_tool()` function with singleton pattern
- [ ] Verify Daytona tool can be initialized

### Task 3.2: Add web_search Tool
- [ ] Import `DuckDuckGoSearchRun` from `langchain_community.tools`
- [ ] Create `web_search` tool using `@tool` decorator
- [ ] Test tool can perform search

### Task 3.3: Add data_analysis Tool
- [ ] Create `data_analysis` tool using `@tool` decorator
- [ ] Implement tool to execute Python code in Daytona sandbox
- [ ] Handle exceptions and return formatted results
- [ ] Test tool with simple Python code

### Task 3.4: Verify All Tools
- [ ] Verify `create_task` tool still works
- [ ] Verify `get_tasks` tool still works
- [ ] Verify `web_search` tool works
- [ ] Verify `data_analysis` tool works

**Verification:**
```bash
uv run python -c "
from src.agent.tools import create_task, get_tasks, web_search, data_analysis
print('All tools imported successfully')
print('create_task:', create_task.name)
print('get_tasks:', get_tasks.name)
print('web_search:', web_search.name)
print('data_analysis:', data_analysis.name)
"
```

---

## Phase 4: DeepAgent Creation

### Task 4.1: Refactor graph.py - Import DeepAgent
- [ ] Import `create_deep_agent` from `deepagents`
- [ ] Import `ChatOllama` from `langchain_ollama`
- [ ] Remove old StateGraph imports (if not needed)

### Task 4.2: Implement Model Fallback
- [ ] Create `get_model()` function
- [ ] Implement primary model: `qwen3.5:cloud` with Ollama Cloud
- [ ] Implement fallback model: `llama3.2:3b` local
- [ ] Add error handling for cloud model failures

### Task 4.3: Configure Tools
- [ ] Create `TOOLS` list with all tools
- [ ] Verify all 4 tools are included

### Task 4.4: Create System Prompt
- [ ] Write system prompt describing agent capabilities
- [ ] Document all available tools
- [ ] Add guidelines for WhatsApp response length

### Task 4.5: Create DeepAgent
- [ ] Create `create_whatsapp_agent()` function
- [ ] Use `create_deep_agent()` with model, tools, system_prompt
- [ ] Export `app` variable for webhook use

### Task 4.6: Test DeepAgent Creation
- [ ] Verify agent can be created without errors
- [ ] Test agent invocation with simple message

**Verification:**
```bash
uv run python -c "
from src.agent.graph import app, get_model
print('Agent created successfully')
model = get_model()
print('Model:', model.model)
"
```

---

## Phase 5: Webhook Handler

### Task 5.1: Verify Import Works
- [ ] Verify `from src.agent.graph import app` works in `main.py`
- [ ] Check that invocation pattern is compatible

### Task 5.2: Test Webhook Endpoint
- [ ] Run FastAPI server
- [ ] Test webhook with task creation message
- [ ] Test webhook with web search query
- [ ] Test webhook with data analysis query

**Verification:**
```bash
# Start server in one terminal
uv run uvicorn main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test webhook (requires server running)
curl -X POST http://localhost:8000/webhook \
  -d "Body=What is the capital of France?" \
  -d "From=whatsapp:+1234567890"
```

---

## Phase 6: Testing

### Task 6.1: Run Existing Tests
- [ ] Run `uv run pytest -v` to verify existing tests pass
- [ ] Fix any broken tests (may need to update for DeepAgent)

### Task 6.2: Test Task Management
- [ ] Test task creation: "Ask John to finish the report by Friday"
- [ ] Test task query: "How many tasks does John have?"

### Task 6.3: Test Web Search
- [ ] Test simple search: "What is the capital of France?"
- [ ] Test complex search: "Who won the latest Super Bowl?"

### Task 6.4: Test Data Analysis
- [ ] Test mathematical calculation: "Calculate 2+2"
- [ ] Test complex math: "Calculate compound interest for 1000 at 5% for 5 years"
- [ ] Test visualization: "Create a bar chart of [1,2,3,4,5]"

### Task 6.5: Run Lint and Type Check
- [ ] Run `uv run ruff check . --fix`
- [ ] Run `uv run mypy .`
- [ ] Fix any lint or type errors

**Verification:**
```bash
# Run all tests
uv run pytest -v

# Run lint
uv run ruff check . --fix

# Run type check
uv run mypy .
```

---

## Deprecation Tasks

### Task D.1: Deprecate router.py
- [ ] Add deprecation warning comment to `src/agent/router.py`
- [ ] Document that LLM now handles intent classification

### Task D.2: Preserve Original Implementation
- [ ] Optionally copy original `graph.py` to `graph_original.py` for rollback reference

---

## Documentation Tasks

### Task Doc.1: Update AGENTS.md
- [ ] Update AGENTS.md to reflect new DeepAgent architecture
- [ ] Document new tools and capabilities

### Task Doc.2: Update README.md
- [ ] Update README.md with new features if needed

---

## Rollback Plan

If issues arise:
1. Keep original `graph.py` saved as `graph_original.py`
2. Revert imports in `main.py` to use original agent
3. Remove new tool definitions from `tools.py` if needed

---

## Implementation Order Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | 1.1 - 1.2 | 5 min |
| Phase 2 | 2.1 | 5 min |
| Phase 3 | 3.1 - 3.4 | 15 min |
| Phase 4 | 4.1 - 4.6 | 15 min |
| Phase 5 | 5.1 - 5.2 | 10 min |
| Phase 6 | 6.1 - 6.5 | 20 min |
| Deprecation | D.1 - D.2 | 5 min |
| Documentation | Doc.1 - Doc.2 | 10 min |

**Total Estimated Time: ~85 minutes**
