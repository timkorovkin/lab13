import asyncio
import json
import logging
from nats.aio.client import Client as NATS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def run():
    nc = NATS()

    await nc.connect("nats://localhost:4222")
    logger.info("Подключение к NATS успешно")

    async def message_handler(msg):
        result = json.loads(msg.data.decode())
        logger.info(f"Получен результат: {result}")

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
    await nc.close()
    logger.info("Оркестратор завершил работу")

if __name__ == "__main__":
    asyncio.run(run())