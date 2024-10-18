from .database import db


scores_collection = db["scores"]
outbox_collection = db["outbox_messages"]