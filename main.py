"""FastAPI webhook server for WhatsApp task management agent.

This module creates a FastAPI application that handles incoming WhatsApp
messages via Twilio webhooks and processes them through the LangGraph agent.

Usage:
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse  # type: ignore[import-untyped]

from src.db.database import create_tables

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize database on startup."""
    create_tables()
    yield


app = FastAPI(
    title="WhatsApp Task Agent",
    description="A LangGraph-powered WhatsApp agent for task management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Status message indicating the server is running.
    """
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook_endpoint(
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
) -> Response:
    """Twilio WhatsApp webhook endpoint.

    Receives incoming WhatsApp messages from Twilio, processes them
    through the task management agent, and returns a TwiML response.

    Args:
        From: Sender's WhatsApp number (e.g., whatsapp:+14155238886).
        To: Recipient's WhatsApp number.
        Body: Message text content.

    Returns:
        TwiML XML response to send back to WhatsApp user.
    """
    if not From or not Body:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: From and Body are required",
        )

    message = Body.strip()
    if not message:
        twiml = _create_twiml("I didn't receive any message. Please try again.")
        return Response(content=str(twiml), media_type="text/xml")

    from src.agent.graph import app as agent_app
    from langchain_core.messages import HumanMessage
    from langchain_core.tracers import LangChainTracer

    tracer = LangChainTracer(project_name="whatsapp-task-agent")

    result = agent_app.invoke(
        {"messages": [HumanMessage(content=message)]},
        config={"callbacks": [tracer]},
    )  # type: ignore[call-overload]

    response_text = result.get(
        "response", "I'm having trouble processing your request."
    )
    twiml = _create_twiml(response_text)
    return Response(content=str(twiml), media_type="text/xml")


def _create_twiml(message: str) -> MessagingResponse:
    """Create a TwiML MessagingResponse with the given message.

    Args:
        message: The text message to send back.

    Returns:
        TwiML response object.
    """
    twiml = MessagingResponse()
    twiml.message(message)
    return twiml
