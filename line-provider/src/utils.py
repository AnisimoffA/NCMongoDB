import json
from fastapi.exceptions import HTTPException
# from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from .models import events_collection, outbox_collection
from .database import object_id_str
# from sqlalchemy import select
# from .database import async_session_maker
# from .models import Event, OutboxMessageModel
from .schemas import EventStatus, EventCreate, KafkaEvent
# from sqlalchemy.ext.asyncio import AsyncSession
from bson import ObjectId


class EventUsefulMethods:
    @staticmethod
    def to_utc_time(current_deadline):
        correct_deadline = (current_deadline.
                            astimezone(timezone.utc).replace(tzinfo=None))
        return correct_deadline


class EventDBMethods:
    @staticmethod
    async def select_all_events() -> list:
        items = []
        async for item in events_collection.find():
            items.append(object_id_str(item))
        return items

    @staticmethod
    async def select_event_by_id(event_id: str):
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid item ID")
        item = await events_collection.find_one({"_id": ObjectId(event_id)})
        if item:
            return object_id_str(item)
        raise HTTPException(status_code=404, detail="Item not found")

    @staticmethod
    async def update_event_status(event_id: str, status: EventStatus):
        event = await events_collection.find_one({"_id": ObjectId(event_id)})

        if event:
            updated_event = await events_collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"status": status.value}}
            )

            if updated_event.modified_count == 1:
                return {"msg": "Event status updated successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to update event status")
        else:
            raise HTTPException(status_code=404, detail="Event not found")
#
    @staticmethod
    async def insert_into_event(event: EventCreate, utc_deadline: datetime):
        item_dict = event.dict(by_alias=True)
        item_dict['deadline'] = utc_deadline
        result = await events_collection.insert_one(item_dict)
        created_item = await events_collection.find_one({"_id": result.inserted_id})
        return object_id_str(created_item)


class KafkaMethods:
    @staticmethod
    async def send_score_update_error_message(row_id):
        try:
            data = KafkaEvent(
                data={"row_id": row_id},
                event="score_update",
                status="error"
            )

            new_event = {
                "occurred_on": datetime.now(timezone.utc),
                "status": "in process",
                "data": json.dumps(data.dict())
            }

            result = await outbox_collection.insert_one(new_event)

            if result.inserted_id:
                return {"message": "Event inserted successfully", "id": str(result.inserted_id)}
            else:
                raise HTTPException(status_code=500, detail="Failed to insert event")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

