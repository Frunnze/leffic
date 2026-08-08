import os

_ = os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret-key-value")
_ = os.environ.setdefault("DATABASE_URL", "sqlite://")
