from pymongo import MongoClient
import os


client = MongoClient(f"mongodb://{os.getenv('MONGODB_HOST')}")
db = client["fsrs_db"]
