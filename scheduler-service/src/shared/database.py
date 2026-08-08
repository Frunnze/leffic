import os

from pymongo import MongoClient
from pymongo.database import Database

MongoDocument = dict[str, object]

client: MongoClient[MongoDocument] = MongoClient(
    f"mongodb://{os.getenv('MONGODB_HOST')}"
)
db: Database[MongoDocument] = client["fsrs_db"]
