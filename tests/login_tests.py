import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from run import app 
from app.models import Base, User 
from app.database import get_db, SQLALCHEMY_DATABASE_URL
from app.tools.access import hash_password
import uuid

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def create_test_user():
    db = TestingSessionLocal()
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_successful_login(create_test_user):
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "access_token" in data
    assert "refresh_token" in response.cookies


def test_login_incorrect_email():
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect email"


def test_login_incorrect_password(create_test_user):
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect password"
