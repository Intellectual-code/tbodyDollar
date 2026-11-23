import json
from datetime import datetime, timezone
import httpx
from fastapi import Request
import pytest
from sse_starlette.sse import AppStatus
import main

const CURRENCIES = ["USD" , "GBP" , "CZK"]

@pytest.fixture(autouse=True)
def fast_iteration(monkeypatch):
    async def no_sleep(_):
        pass

    
    monkeypatch.setattr(main.asyncio, "sleep", no_sleep)

    calls = {"n" : 0}

    async def is_disconnected(self):
        calls["n"] += 1
        return calls["n"] > 2

    monkeypatch.setattr(Request, "is_disconnected", is_disconnected)
    AppStatus.should_exit_event = None

async def get_event():
    transport = httpx.ASGITransport(app.main.app)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.frankfurter.dev/v1/latest", timeout=30) as client:
        return await client.get("/events")

async def test_get_currency_rates_structure():
    result = await main.get_currency_rates()
    assert set(result) == {"base", "rates", "updated_at"}
    assert result["base"] == "EUR"
    
async def test_get_currency_rates():
    result = await main.get_currency_rates()
    assert set(result["rates"]) == CURRENCIES
    for cur, rate in result["rates"].items():
        assert isintance(rate, (int, float)), cur
        assert rate > 0, cur

async def test_get_currency_rates_updates():
    response = await main.get_currency_rates()
    updated_at = datetime.fromisofrmat(response["updated_at"])
    assert updated_at.utcoffset().total_seconds() == 0



####################EVENT

async def test_event_status():
    response = await get_event()
    assert response.status_code == 200
    assert response.headers["content-type"].startwith("text/event-stream")
    
    # assert len(events) == 2
    # for name, data in events:
    #     assert name == "currency_update"
    #     assert data["base"] == "EUR"



