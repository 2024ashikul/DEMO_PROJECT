# Import pytest testing framework
import pytest
# Import TestClient from fastapi.testclient
from fastapi.testclient import TestClient
# Import SQLAlchemy tools to set up test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
# Import application instance, Base model, and get_db dependency
from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite database with StaticPool for test execution isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create SQLAlchemy engine using StaticPool to maintain single connection in memory
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session factory for testing database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    Dependency override providing isolated SQLite test database session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override FastAPI get_db dependency with test database provider
app.dependency_overrides[get_db] = override_get_db

# Initialize TestClient
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_database():
    """
    Pytest fixture running before each test to create clean database tables and dropping them after completion.
    """
    # Create tables in test database
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test completes
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """
    Test GET /health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "auth-service"}

def test_register_user_success():
    """
    Test POST /register endpoint with database persistence.
    """
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_username():
    """
    Test POST /register endpoint when registering a duplicate username.
    """
    payload = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "password123"
    }
    res1 = client.post("/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Username already registered"

def test_login_success():
    """
    Test POST /token endpoint against database records.
    """
    reg_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123"
    }
    client.post("/register", json=reg_payload)

    login_payload = {
        "username": "loginuser",
        "password": "password123"
    }
    response = client.post("/token", json=login_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password():
    """
    Test POST /token endpoint with incorrect password.
    """
    reg_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "correctpassword"
    }
    client.post("/register", json=reg_payload)

    login_payload = {
        "username": "loginuser",
        "password": "wrongpassword"
    }
    response = client.post("/token", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_get_current_user_profile():
    """
    Test GET /me endpoint using Bearer token dependency and database lookup.
    """
    reg_payload = {
        "username": "profileuser",
        "email": "profile@example.com",
        "password": "password123"
    }
    client.post("/register", json=reg_payload)

    login_res = client.post("/token", json={"username": "profileuser", "password": "password123"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profileuser"
    assert data["email"] == "profile@example.com"

def test_get_current_user_unauthorized():
    """
    Test GET /me endpoint without authorization header.
    """
    response = client.get("/me")
    assert response.status_code in [401, 403]
