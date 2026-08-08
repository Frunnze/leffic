import os

from pymongo import MongoClient
from pymongo.database import Database

MongoDocument = dict[str, object]

_MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost:27017")

client: MongoClient[MongoDocument] = MongoClient(
    f"mongodb://{_MONGODB_HOST}"
)
db: Database[MongoDocument] = client["fsrs_db"]


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
