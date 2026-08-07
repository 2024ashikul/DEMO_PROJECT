# Import pytest testing framework
import pytest
# Import PyJWT to generate test access tokens dynamically
import jwt
# Import TestClient from fastapi.testclient
from fastapi.testclient import TestClient
# Import SQLAlchemy tools to set up test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
# Import user-service application objects and Base/get_db
from app.main import app
from app.database import Base, get_db
from app.auth import SECRET_KEY, ALGORITHM

# Use SQLite in-memory database with StaticPool for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply database override
app.dependency_overrides[get_db] = override_get_db

# Initialize FastAPI TestClient
client = TestClient(app)

def create_mock_jwt(username: str = "alice", email: str = "alice@example.com") -> str:
    """
    Helper function to encode a valid test JWT token using shared SECRET_KEY.
    """
    payload = {"sub": username, "email": email}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture(autouse=True)
def setup_test_database():
    """
    Pytest fixture creating tables before each test and dropping after completion.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """
    Test GET /health endpoint for user-service.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "user-service"}

def test_get_user_profile_success():
    """
    Test GET /users/profile endpoint with valid Bearer token.
    """
    token = create_mock_jwt("alice", "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/profile", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "full_name" in data
    assert "bio" in data
    assert "location" in data

def test_update_user_profile_success():
    """
    Test PUT /users/profile endpoint to update full name and bio in database.
    """
    token = create_mock_jwt("bob", "bob@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "full_name": "Bob Smith",
        "bio": "Lead Cloud Architect",
        "location": "New York, USA"
    }

    response = client.put("/users/profile", json=update_payload, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "bob"
    assert data["full_name"] == "Bob Smith"
    assert data["bio"] == "Lead Cloud Architect"
    assert data["location"] == "New York, USA"

    # Fetch profile via GET to verify database persistence
    get_res = client.get("/users/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["bio"] == "Lead Cloud Architect"

def test_get_profile_unauthorized():
    """
    Test GET /users/profile endpoint without authorization header.
    """
    response = client.get("/users/profile")
    assert response.status_code in [401, 403]
