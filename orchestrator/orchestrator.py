import asyncio
import json
import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/orchestrator.log")
    ]
)
logger = logging.getLogger(__name__)

processed_count = 0

async def run():
    global processed_count
    from nats.aio.client import Client as NATS
    nc = NATS()

    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    await nc.connect(nats_url)
    logger.info("Подключение к NATS успешно")

    async def message_handler(msg):
        global processed_count
        result = json.loads(msg.data.decode())
        processed_count += 1
        logger.info(f"Получен результат: {result} | Обработано задач: {processed_count}")

    await nc.subscribe("resume.parsed", cb=message_handler)

    resumes = [
        {"name": "Иван Иванов", "experience_years": 1, "skills": ["Go", "Docker"], "education": "БГУИР"},
        {"name": "Мария Петрова", "experience_years": 4, "skills": ["Python", "FastAPI"], "education": "БГУ"},
        {"name": "Алексей Сидоров", "experience_years": 7, "skills": ["Go", "Kubernetes"], "education": "БНТУ"},
    ]

    for resume in resumes:
        data = json.dumps(resume).encode()
        await nc.publish("resume.parse", data)
        logger.info(f"Отправлено резюме: {resume['name']}")
        await asyncio.sleep(0.5)

    await asyncio.sleep(2)
    logger.info(f"Оркестратор завершил работу. Всего обработано задач: {processed_count}")
    await nc.close()

if __name__ == "__main__":
    asyncio.run(run())