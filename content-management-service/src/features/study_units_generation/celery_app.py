import os

from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST")

celery_app = Celery(
    "content",
    broker=f"redis://{REDIS_HOST}",
    backend=f"redis://{REDIS_HOST}",
    include=["features.study_units_generation.generation_tasks"],
)
