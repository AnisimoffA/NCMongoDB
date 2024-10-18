import aiohttp
import json

from bson import ObjectId
from fastapi.exceptions import HTTPException
from dateutil import parser
from datetime import datetime, timezone
from sqlalchemy import select
from .database import db, object_id_str, client
from .models import scores_collection, outbox_collection
from .config import LP_URL, LP_PORT
from .schemas import KafkaEvent
from sqlalchemy.ext.asyncio import AsyncSession


class EventUsefulMethods:
    def to_utc_time(current_deadline):
        correct_deadline = parser.isoparse(current_deadline)
        return correct_deadline.replace(tzinfo=timezone.utc)


class EventRemoteMethods:
    @staticmethod
    async def fetch_from_service(url: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Ошибка при получении данных"
                        )
                    return await response.json()
            except aiohttp.ClientError:
                raise HTTPException(
                    status_code=500,
                    detail="Ошибка коммуникации с внешним сервисом"
                )

    @staticmethod
    async def get_all_events():
        return await EventRemoteMethods.fetch_from_service(
            f"http://{LP_URL}:{LP_PORT}/events"
        )

    @staticmethod
    async def get_event_by_id(event_id: str):
        print(f"http://{LP_URL}:{LP_PORT}/events/{event_id}")
        return await EventRemoteMethods.fetch_from_service(
            f"http://{LP_URL}:{LP_PORT}/events/{event_id}"
        )


class ScoreDBMethods:
    @staticmethod
    async def select_all_scores() -> list:
        items = []
        async for item in scores_collection.find():
            items.append(object_id_str(item))
        return items

    @staticmethod
    async def insert_into_score(event_id: int, score: str):
        session = await client.start_session()
        try:
            # Вставка новой оценки в коллекцию "scores"
            new_score = {
                "event_id": event_id,
                "score": score
            }
            result = await scores_collection.insert_one(new_score)
            row_id = result.inserted_id

            # Создание KafkaEvent для outbox
            data = KafkaEvent(
                data={
                    "event_id": event_id,
                    "event_score": score,
                    "row_id": str(row_id)
                },
                event="score_insert_into_db",
                status="success"
            )

            # Вставка нового события в коллекцию "outbox_messages"
            new_event = {
                "occurred_on": datetime.now(timezone.utc),
                "status": "in process",
                "data": json.dumps(data.dict())
            }
            await outbox_collection.insert_one(new_event)

            return {"status": "success"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to insert score: {str(e)}")

    @staticmethod
    async def delete_from_score(row_id: str):
        await scores_collection.delete_one({"_id": ObjectId(row_id)})


class EventValidator:
    @staticmethod
    def validate_deadline(deadline):
        if deadline < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=400,
                detail="Событие нельзя оценить")


class ScoreMethods:
    @staticmethod
    def check_actuality(events):
        returned_events = []
        for event in events:
            deadline = parser.isoparse(event["deadline"])
            deadline = deadline.replace(tzinfo=timezone.utc)
            if deadline > datetime.now(timezone.utc):
                returned_events.append(event)
        return returned_events
