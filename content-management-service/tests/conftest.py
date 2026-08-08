import os

_ = os.environ.setdefault("DATABASE_URL", "sqlite://")
_ = os.environ.setdefault("SCHEDULER_SERVICE", "http://scheduler")
