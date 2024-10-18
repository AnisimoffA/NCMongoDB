import motor.motor_asyncio
from .config import MONGODB_HOST, MONGODB_PASS, MONGODB_PORT, MONGODB_USER


MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource=admin"
DATABASE_NAME = "score-maker"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]


def object_id_str(obj):
    if "_id" in obj:
        obj["id"] = str(obj["_id"])
        del obj["_id"]
    return obj

#