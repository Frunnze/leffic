from celery import Celery

from shared.settings import REDIS_HOST

celery_app = Celery(
    "app",
    broker=f"redis://{REDIS_HOST}",
    backend=f"redis://{REDIS_HOST}",
    include=["features.study_units_generation.generation_tasks"],
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
