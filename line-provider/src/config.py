from dotenv import load_dotenv
import os
import asyncio

loop = asyncio.get_event_loop()
load_dotenv('.env.prod')

KAFKA_TOPIC_SCORE_MAKER = os.getenv('KAFKA_TOPIC_SCORE_MAKER')
KAFKA_TOPIC_LINE_PROVIDER = os.getenv('KAFKA_TOPIC_LINE_PROVIDER')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASS = os.getenv("MONGODB_PASS")
