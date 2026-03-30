"""Async tests for webhook endpoint using httpx and pytest-asyncio."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client for the FastAPI app."""
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_health_check_async(async_client):
    """Test health check endpoint with async client."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_webhook_valid_request_async(async_client):
    """Test webhook processes valid request with async client."""
    response = await async_client.post(
        "/webhook",
        data={
            "From": "whatsapp:+14155238886",
            "To": "whatsapp:+14155238887",
            "Body": "Hello!",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/xml; charset=utf-8"
    assert "<Message>" in response.text


@pytest.mark.asyncio
async def test_webhook_missing_body_async(async_client):
    """Test webhook returns 400 when Body is missing."""
    response = await async_client.post(
        "/webhook",
        data={"From": "whatsapp:+14155238886"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_create_task_async(async_client):
    """Test create task flow via async webhook."""
    response = await async_client.post(
        "/webhook",
        data={
            "From": "whatsapp:+14155238886",
            "To": "whatsapp:+14155238887",
            "Body": "Ask John to finish the report by Friday",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/xml; charset=utf-8"
    assert "<Message>" in response.text
