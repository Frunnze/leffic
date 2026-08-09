import os

_ = os.environ.setdefault("REDIS_HOST", "localhost:6379")
_ = os.environ.setdefault("CONTENT_MANAGEMENT_SERVICE", "http://content")
_ = os.environ.setdefault("OPENAI_API_KEY", "test-key")
