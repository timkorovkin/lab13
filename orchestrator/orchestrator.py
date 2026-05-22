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
TIMEOUT = 5
MAX_RETRIES = 3

async def send_with_retry(nc, resume):
    global processed_count

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Отправка резюме: {resume['name']} (попытка {attempt})")

            future = asyncio.get_event_loop().create_future()

            async def handler(msg):
                if not future.done():
                    future.set_result(json.loads(msg.data.decode()))

            sub = await nc.subscribe("resume.parsed", cb=handler)

            await nc.publish("resume.parse", json.dumps(resume).encode())

            result = await asyncio.wait_for(future, timeout=TIMEOUT)

            await sub.unsubscribe()
            processed_count += 1
            logger.info(f"Результат получен: {result} | Обработано задач: {processed_count}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"Таймаут ожидания результата для {resume['name']} (попытка {attempt})")
            if attempt == MAX_RETRIES:
                logger.error(f"Все {MAX_RETRIES} попытки исчерпаны для {resume['name']}")
                return None

        except Exception as e:
            logger.error(f"Ошибка при обработке {resume['name']}: {e} (попытка {attempt})")
            if attempt == MAX_RETRIES:
                return None

        await asyncio.sleep(1)

async def run():
    from nats.aio.client import Client as NATS
    nc = NATS()

    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    await nc.connect(nats_url)
    logger.info("Подключение к NATS успешно")

    resumes = [
        {"name": "Иван Иванов", "experience_years": 1, "skills": ["Go", "Docker"], "education": "БГУИР"},
        {"name": "Мария Петрова", "experience_years": 4, "skills": ["Python", "FastAPI"], "education": "БГУ"},
        {"name": "Алексей Сидоров", "experience_years": 7, "skills": ["Go", "Kubernetes"], "education": "БНТУ"},
    ]

    for resume in resumes:
        await send_with_retry(nc, resume)
        await asyncio.sleep(0.5)

    logger.info(f"Оркестратор завершил работу. Всего обработано задач: {processed_count}")
    await nc.close()

if __name__ == "__main__":
    asyncio.run(run())