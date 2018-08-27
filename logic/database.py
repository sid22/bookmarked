import pymongo
from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI)
db = client.bookmarked
