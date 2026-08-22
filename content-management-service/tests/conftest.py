import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SCHEDULER_SERVICE"] = "http://scheduler"
os.environ["REDIS_HOST"] = "localhost:6379"
os.environ["OPENAI_API_KEY"] = "test-key-never-a-real-one"
