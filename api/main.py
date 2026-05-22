import asyncio
import json
import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from nats.aio.client import Client as NATS

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log")
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="HR System API")
nc = NATS()

class Resume(BaseModel):
    name: str
    experience_years: int
    skills: list[str]
    education: str

@app.on_event("startup")
async def startup():
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    await nc.connect(nats_url)
    logger.info("API подключено к NATS")

@app.on_event("shutdown")
async def shutdown():
    await nc.close()

@app.post("/parse-resume")
async def parse_resume(resume: Resume):
    logger.info(f"Получен запрос на обработку резюме: {resume.name}")

    future = asyncio.get_event_loop().create_future()

    async def handler(msg):
        if not future.done():
            future.set_result(json.loads(msg.data.decode()))

    sub = await nc.subscribe("resume.parsed", cb=handler)

    await nc.publish("resume.parse", resume.model_dump_json().encode())

    try:
        result = await asyncio.wait_for(future, timeout=5.0)
        await sub.unsubscribe()
        logger.info(f"Результат отправлен клиенту: {result}")
        return result
    except asyncio.TimeoutError:
        await sub.unsubscribe()
        logger.error(f"Таймаут обработки резюме: {resume.name}")
        raise HTTPException(status_code=504, detail="Таймаут ожидания ответа от агента")

@app.get("/health")
async def health():
    return {"status": "ok"}