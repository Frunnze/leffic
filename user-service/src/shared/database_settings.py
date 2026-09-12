import os

POSTGRES_SCHEME = "postgresql"

DATABASE_NAME = "users"
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASS", "postgres")
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_PORT = os.getenv("DB_PORT", "5455")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"{POSTGRES_SCHEME}://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)
