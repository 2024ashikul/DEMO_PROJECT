# Import pytest testing framework
import pytest
# Import PyJWT to generate mock access tokens for authenticated endpoints
import jwt
# Import TestClient from fastapi.testclient
from fastapi.testclient import TestClient
# Import SQLAlchemy tools to set up test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
# Import task-service application objects and Base/get_db
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

# Initialize TestClient
client = TestClient(app)

def create_mock_jwt(username: str = "charlie") -> str:
    """
    Helper function to encode a valid JWT token payload for testing.
    """
    payload = {"sub": username, "email": f"{username}@example.com"}
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
    Test GET /health endpoint for task-service.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "task-service"}

def test_create_task_success():
    """
    Test POST /tasks endpoint to create a new task in database.
    """
    token = create_mock_jwt("charlie")
    headers = {"Authorization": f"Bearer {token}"}

    task_payload = {
        "title": "Build FastAPI Microservices",
        "description": "Create 3 separate Docker containers and Pytest suites",
        "completed": False
    }

    response = client.post("/tasks", json=task_payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Build FastAPI Microservices"
    assert data["owner_username"] == "charlie"
    assert data["completed"] is False
    assert "id" in data

def test_get_user_tasks_isolation():
    """
    Test GET /tasks endpoint ensuring users only see their own tasks in database.
    """
    # Create task for user 'charlie'
    token_charlie = create_mock_jwt("charlie")
    client.post(
        "/tasks",
        json={"title": "Charlie's Secret Task"},
        headers={"Authorization": f"Bearer {token_charlie}"}
    )

    # Create task for user 'dave'
    token_dave = create_mock_jwt("dave")
    client.post(
        "/tasks",
        json={"title": "Dave's Task"},
        headers={"Authorization": f"Bearer {token_dave}"}
    )

    # Fetch tasks for 'charlie'
    res_charlie = client.get("/tasks", headers={"Authorization": f"Bearer {token_charlie}"})
    assert res_charlie.status_code == 200
    charlie_tasks = res_charlie.json()
    assert len(charlie_tasks) == 1
    assert charlie_tasks[0]["title"] == "Charlie's Secret Task"

    # Fetch tasks for 'dave'
    res_dave = client.get("/tasks", headers={"Authorization": f"Bearer {token_dave}"})
    assert res_dave.status_code == 200
    dave_tasks = res_dave.json()
    assert len(dave_tasks) == 1
    assert dave_tasks[0]["title"] == "Dave's Task"

def test_update_and_delete_task():
    """
    Test PUT /tasks/{id} and DELETE /tasks/{id} endpoints against database records.
    """
    token = create_mock_jwt("charlie")
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    create_res = client.post("/tasks", json={"title": "Initial Title"}, headers=headers)
    task_id = create_res.json()["id"]

    # Update task
    update_res = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "completed": True},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"
    assert update_res.json()["completed"] is True

    # Delete task
    del_res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify task is deleted
    get_res = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 404
