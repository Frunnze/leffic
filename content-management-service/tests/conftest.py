import os

_ = os.environ.setdefault("DATABASE_URL", "sqlite://")
_ = os.environ.setdefault("SCHEDULER_SERVICE", "http://scheduler")
_ = os.environ.setdefault("REDIS_HOST", "localhost:6379")
_ = os.environ.setdefault("OPENAI_API_KEY", "test-key")
