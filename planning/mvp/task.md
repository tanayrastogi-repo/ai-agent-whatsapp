# Project TODO

## Phase 1: Environment, Tooling & DB Setup

- [x] Initialize project with `uv init`
- [x] Create virtual environment with `uv venv`
- [x] Add core dependencies:
  - [x] langchain, langgraph
  - [x] sqlalchemy
  - [x] fastapi, uvicorn
  - [x] pydantic
  - [x] twilio
- [x] Add dev dependencies:
  - [x] pytest, pytest-asyncio
  - [x] httpx
  - [x] ruff, black, mypy
- [x] Set up `.python-version` (3.11+)
- [x] Create `.env` file with required environment variables
- [x] Verify Ollama is running locally
- [x] Define SQLAlchemy models for tasks
- [x] Create SQLite database and tables
- [x] Verify DB connection works
- [x] **Verify Phase 1 Completion:** Run `uv run pytest` to ensure no errors, update README.md with Phase 1 summary

## Observability: LangSmith Integration

- [x] Add LangSmith environment variables to `.env`
- [x] Create `src/agent/langsmith_config.py` for tracing configuration
- [x] Export LangSmith config functions in `src/agent/__init__.py`
- [x] Verify LangSmith is integrated (env vars auto-enable tracing with LangChain)

## Phase 2: The Agent Tools & LangGraph

- [x] Set up Ollama LLM connection with ChatOllama
- [x] Define state schema (AgentState with messages, intent, tool_result)
- [x] Build `create_task` tool (parse text, insert into DB)
- [x] Build `get_tasks` tool (query DB by assignee/dates)
- [x] Implement LLM router node (classify intent: create/query/clarify)
- [x] Implement ResponseBuilder node (format tool results to natural language)
- [x] Construct LangGraph state machine with conditional edges
- [x] Test tool calling with Ollama LLM
- [x] **Verify Phase 2 Completion:** Test tools manually, update README.md with Phase 2 summary

## Phase 3: The Webhook Server (FastAPI)

- [x] Create FastAPI application entry point
- [x] Implement POST endpoint for Twilio webhooks
- [x] Integrate LangGraph agent with webhook endpoint
- [x] Return Twilio-formatted XML (TwiML) responses
- [x] Handle incoming message parsing
- [x] Add error handling for webhook requests
- [x] Test with local FastAPI server
- [x] **Verify Phase 3 Completion:** Start server with `uv run uvicorn main:app`, update README.md with Phase 3 summary

## Phase 4: Functional Testing

- [x] Set up test directory structure
- [x] Create `conftest.py` with pytest fixtures
- [x] Write tests for `create_task` tool
- [x] Write tests for `get_tasks` tool
- [x] Write tests for webhook endpoint (simulate Twilio requests)
- [x] Add integration tests for full flow
- [x] Run test suite and verify all tests pass
- [x] **Verify Phase 4 Completion:** All tests pass with `uv run pytest -v`, update README.md with Phase 4 summary

## Phase 5: Connecting Twilio + Ngrok

### Prerequisites
1. **Twilio Account**: Sign up at https://www.twilio.com/try-twilio
2. **WhatsApp Account**: Install WhatsApp on your phone
3. **Ngrok Account**: Sign up at https://ngrok.com for a free account

### Step-by-Step Implementation

#### 1. Install and Configure Ngrok
```bash
# Download ngrok (macOS)
brew install ngrok

# OR download for other platforms from https://ngrok.com/download

# Connect your ngrok account (get authtoken from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken <your-authtoken>
```

#### 2. Join Twilio WhatsApp Sandbox
1. Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **Confirm** to acknowledge the terms
3. Send `join <sandbox-code>` to `whatsapp:+14155238886` from your phone
   - Example: If your sandbox code is "XY123ABC", send: `join XY123ABC`
4. You'll receive a confirmation: "You have successfully subscribed to WhatsApp notifications!"

#### 3. Update .env with Twilio Credentials
```bash
# Get these from https://console.twilio.com/
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+14155238886  # Sandbox number
```

#### 4. Run the Application
```bash
# Terminal 1: Start FastAPI server
uv run uvicorn main:app --reload --port 8000

# Terminal 2: Start ngrok tunnel
ngrok http 8000

# Note the ngrok URL (e.g., https://abc123xyz.ngrok.io)
```

#### 5. Configure Twilio Sandbox Webhook
1. Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **Sandbox settings**
3. In **When a message comes in**, enter your ngrok URL + `/webhook`
   - Example: `https://abc123xyz.ngrok.io/webhook`
4. Click **Save**

#### 6. Test End-to-End Messaging
Send WhatsApp messages to `whatsapp:+14155238886`:

**Test Task Creation:**
```
Ask John to finish the report by Friday
```
Expected response: "Done! I've created a task for John: 'finish the report' due [date]."

**Test Task Query:**
```
How many tasks does John have?
```
Expected response: "Found 1 task for John: 'finish the report' due [date]"

**Test Clarification:**
```
Hello!
```
Expected response: "I'm a task management assistant. You can: ..."

- [x] Install and configure Ngrok
- [x] Run Ngrok to expose FastAPI server
- [x] Configure Twilio Sandbox webhook URL
- [x] Test end-to-end WhatsApp messaging
- [x] Verify task creation via WhatsApp
- [x] Verify task queries via WhatsApp
- [ ] **Verify Phase 5 Completion:** Send test WhatsApp messages, update README.md with Phase 5 summary

## Optional Enhancements (Out of Scope for PoC)

- [ ] Add task status updates (complete/pending)
- [ ] Add task deletion functionality
- [ ] Implement natural language date parsing improvements
- [ ] Add multiple assignee support
- [ ] Add task priority levels
