import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

TIMEOUT = 5
MAX_RETRIES = 3

async def send_with_retry_mock(nc, resume):
    processed_count = 0
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            future = asyncio.get_event_loop().create_future()

            async def handler(msg):
                if not future.done():
                    future.set_result(json.loads(msg.data.decode()))

            sub = await nc.subscribe("resume.parsed", cb=handler)
            await nc.publish("resume.parse", json.dumps(resume).encode())
            result = await asyncio.wait_for(future, timeout=TIMEOUT)
            await sub.unsubscribe()
            processed_count += 1
            return result
        except asyncio.TimeoutError:
            if attempt == MAX_RETRIES:
                return None
        await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_successful_processing():
    nc = AsyncMock()
    result_data = {"name": "Иван Иванов", "level": "junior", "skills": ["Go"]}

    async def mock_subscribe(topic, cb):
        msg = MagicMock()
        msg.data = json.dumps(result_data).encode()
        asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(cb(msg)))
        sub = AsyncMock()
        return sub

    nc.subscribe = mock_subscribe

    resume = {"name": "Иван Иванов", "experience_years": 1, "skills": ["Go"], "education": "БГУИР"}
    result = await send_with_retry_mock(nc, resume)

    assert result is not None
    assert result["name"] == "Иван Иванов"
    assert result["level"] == "junior"

@pytest.mark.asyncio
async def test_timeout_returns_none():
    nc = AsyncMock()

    async def mock_subscribe_no_response(topic, cb):
        sub = AsyncMock()
        return sub

    nc.subscribe = mock_subscribe_no_response

    resume = {"name": "Тест", "experience_years": 1, "skills": [], "education": ""}

    with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
        result = await send_with_retry_mock(nc, resume)

    assert result is None