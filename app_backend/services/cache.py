# hold the cache for the app
# to reduce the cost of repeated calls to the LLM

import redis
from langchain.memory import RedisChatMessageHistory

redis_client = redis.Redis(host='localhost', port=6379, db=0)

memory = RedisChatMessageHistory(redis_client)