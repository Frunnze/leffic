from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


db_name = "users"
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "postgres")
db_host = os.getenv("DB_HOST",  "localhost")
db_port = os.getenv("DB_PORT", 5450)
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

def create_database_if_not_exists():
    try:
        # Connect to the default database to check for the target db
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if DB exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()

        if not exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            cur.execute(f"CREATE DATABASE {db_name}")
        else:
            print(f"Database '{db_name}' already exists.")
    finally:
        cur.close()
        conn.close()


create_database_if_not_exists()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()