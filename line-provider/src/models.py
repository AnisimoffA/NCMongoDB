from .database import db


events_collection = db["events"]
outbox_collection = db["outbox_messages"]
