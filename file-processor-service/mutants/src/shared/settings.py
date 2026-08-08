import os

from dotenv import load_dotenv

_ = load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
CONTENT_MANAGEMENT_SERVICE = os.getenv("CONTENT_MANAGEMENT_SERVICE")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
