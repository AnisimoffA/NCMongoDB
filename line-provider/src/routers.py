from fastapi import APIRouter
from typing import List
from .utils import EventUsefulMethods, EventDBMethods
from .schemas import EventStatus, EventCreate, Event


router_events = APIRouter(tags=["Line-provider"])


@router_events.get("/events", response_model=List[Event])
async def get_items():
    return await EventDBMethods.select_all_events()


@router_events.post("/events")
async def create_event(event: EventCreate):
    utc_deadline = EventUsefulMethods.to_utc_time(event.deadline)
    return await EventDBMethods.insert_into_event(event, utc_deadline)


@router_events.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    return await EventDBMethods.select_event_by_id(event_id)


@router_events.put("/events/{event_id}/status")
async def update_event_status(event_id: str, new_status: EventStatus):
    await EventDBMethods.update_event_status(event_id, new_status)
    return {"status": "Статус обновлен"}