import asyncio
from redis import Redis
from fastapi import FastAPI
from .routers import router_events
from .consumer import consume
from .producer import router_producer, send_events_to_kafka
from .config import REDIS_HOST, REDIS_PORT
from fastapi_utils.tasks import repeat_every
from .database import db


consumer_task = None

app = FastAPI()
app.include_router(router_events)
app.include_router(router_producer)


@app.on_event("startup")
async def startup_event():
    global consumer_task
    consumer_task = asyncio.create_task(consume())

    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    app.state.redis = redis_client

    try:
        await db.command("ping")
        print("Connected to MongoDB")
    except Exception as e:
        print("Failed to connect to MongoDB", e)


@app.on_event("startup")
@repeat_every(seconds=10)  # Периодическая задача раз в 30 секунд
async def process_outbox():
    await send_events_to_kafka()


@app.on_event("shutdown")
async def shutdown_event():
    global consumer_task
    app.state.redis.close()
    if consumer_task:
        consumer_task.cancel()  # Отменяем задачу консюмера
        try:
            await consumer_task  # Ждем завершения задачи
        except asyncio.CancelledError:
            print("Consumer task shutdown successfully")
