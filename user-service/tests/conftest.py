import os

os.environ["JWT_SECRET_KEY"] = "unit-test-secret-key-value"
os.environ["DATABASE_URL"] = "sqlite://"
