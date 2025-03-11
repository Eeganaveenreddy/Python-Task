import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User

# Test database setup (using SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Create a new test database session
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)  # Create tables before each test
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Cleanup after test

# Override the get_db dependency to use the test database
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# Test root endpoint
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}

# Test user creation
def test_create_user(client, db_session):
    user_data = {"name": "Test User", "email": "test@example.com"}
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
    assert response.json()["email"] == "test@example.com"

    # Verify user exists in the database
    user_in_db = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user_in_db is not None
    assert user_in_db.name == "Test User"
