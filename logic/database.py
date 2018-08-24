import pymongo
from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_URI, settings.MONGO_PORT)
db = client.bookmarked