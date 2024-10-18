from aiokafka import AIOKafkaProducer
from fastapi import APIRouter
# from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from .models import outbox_collection
from .config import (KAFKA_BOOTSTRAP_SERVERS,
                     KAFKA_TOPIC_SCORE_MAKER)


router_producer = APIRouter(
    prefix="/kafka_producer",
    tags=["Producer"]
)


# async def get_session() -> AsyncSession:
#     async with async_session_maker() as session:
#         return session


@router_producer.post('/create_message')
async def send_events_to_kafka():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        events_cursor = outbox_collection.find({"status": "in process"})
        events = await events_cursor.to_list(length=None)

        for event in events:
            json_data = event['data'].encode('utf-8')
            await producer.send_and_wait(
                topic=KAFKA_TOPIC_SCORE_MAKER,
                value=json_data
            )
            await outbox_collection.update_one(
                {"_id": event["_id"]},
                {
                    "$set": {
                        "status": "successfully sent",
                        "processed_on": datetime.now(timezone.utc)
                    }
                }
            )
    finally:
        await producer.stop()
