from redis import asyncio as aioredis
from dotenv import load_dotenv
import os
import asyncio


loop = asyncio.get_event_loop()
load_dotenv('.env.prod')

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASS = os.getenv("MONGODB_PASS")

KAFKA_TOPIC_SCORE_MAKER = os.getenv('KAFKA_TOPIC_SCORE_MAKER')
KAFKA_TOPIC_LINE_PROVIDER = os.getenv('KAFKA_TOPIC_LINE_PROVIDER')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')

LP_URL = os.getenv('LP_URL')
LP_PORT = os.getenv('LP_PORT')

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


async def get_redis():
    return await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
