import pymongo
import redis
from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI)
db = client.bookmarked

redis_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
