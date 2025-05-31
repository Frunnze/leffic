import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from types import SimpleNamespace
from datetime import datetime
import uuid

# Import your FastAPI app and the exact auth‐dependency it uses,
# directly from run.py (so you don't import app.dependencies).
from run import app  
from app.models import Base, Folder
from app.database import get_db, SQLALCHEMY_DATABASE_URL

# ─── Database setup ───────────────────────────────────────────────────────────
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ─── Stub out auth to always return our dummy UUID ────────────────────────────
DUMMY_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")

client = TestClient(app)

# ─── Create/drop tables once per module ──────────────────────────────────────
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ─── Pre‑seed a folder for the “duplicate name” test ─────────────────────────
@pytest.fixture
def existing_folder():
    db = TestingSessionLocal()
    f = Folder(
        parent_id="home",
        name="Test Folder",
        user_id=DUMMY_USER_ID,
        created_at=datetime.utcnow()
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    db.close()
    return f

# ─── Tests ────────────────────────────────────────────────────────────────────
def test_create_folder():
    resp = client.post(
        "/create-folder",
        json={"folder_name": "New Folder", "parent_folder_id": "home"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "folder_id" in data
    assert data["folder_name"] == "New Folder"
    assert data["parent_folder_id"] == "home"
    assert data["created_at"]

def test_create_folder_with_same_name(existing_folder):
    resp = client.post(
        "/create-folder",
        json={"folder_name": "Test Folder", "parent_folder_id": "home"}
    )
    assert resp.status_code == 200
    data = resp.json()
    # should have bumped the name
    assert data["folder_name"].startswith("Test Folder")
    assert data["folder_name"] != "Test Folder"

def test_create_folder_invalid_parent():
    resp = client.post(
        "/create-folder",
        json={"folder_name": "Invalid Folder", "parent_folder_id": "nope"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Parent folder not found"

def test_create_folder_without_name():
    resp = client.post(
        "/create-folder",
        json={"parent_folder_id": "home"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["folder_name"] == "New folder"
    assert data["parent_folder_id"] == "home"