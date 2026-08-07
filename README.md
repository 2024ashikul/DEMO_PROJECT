# FastAPI 3-Service Microservices Ecosystem with PostgreSQL & Docker Compose

A complete, production-ready microservices system built with **FastAPI**, **PostgreSQL**, **SQLAlchemy ORM**, **Docker**, **Docker Compose**, **Pytest**, and **GitHub Actions CI/CD**.

---

## 🏛️ System Architecture Overview & Database Design

The system implements the **Database-per-Service** microservice architectural pattern. Each microservice owns its isolated database running inside a centralized, persistent PostgreSQL container (`postgres-db`):

| Container | Service / Database | Port | Description |
| :--- | :--- | :--- | :--- |
| **`postgres-db`** | PostgreSQL 16 DB Engine | `5432` | Runs `auth_db`, `user_db`, and `task_db` with persistent volume (`postgres_data`) |
| **`auth-service`** | Authentication Service | `8001` | User registration, password hashing (bcrypt), JWT generation & verification -> `auth_db` |
| **`user-service`** | User Profile Service | `8002` | User profile retrieval and profile customization -> `user_db` |
| **`task-service`** | Task Management Service | `8003` | Task/Todo management (CRUD operations) -> `task_db` |

```
                       +-------------------------+
                       |   Docker Compose Net    |
                       +------------+------------+
                                    |
      +-----------------------------+-----------------------------+
      |                             |                             |
+-----+-----+                 +-----+-----+                 +-----+-----+
|auth-service|                |user-service|                |task-service|
| Port: 8001 |                | Port: 8002 |                | Port: 8003 |
+------+----+                 +------+----+                 +------+----+
       |                             |                             |
       | DB: auth_db                 | DB: user_db                 | DB: task_db
       +-----------------------------+-----------------------------+
                                     |
                           +---------+---------+
                           |   postgres-db     |
                           |   Port: 5432      |
                           +-------------------+
```

---

## 📂 Project Structure

```
.
├── docker/
│   └── init-dbs.sql         # Automatically initializes auth_db, user_db, and task_db
├── auth-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py          # Hashing (Bcrypt) & JWT creation/decoding
│   │   ├── database.py      # SQLAlchemy database engine & SessionLocal
│   │   ├── main.py          # FastAPI application & auth endpoints
│   │   └── models.py        # SQLAlchemy UserDB model & Pydantic schemas
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_auth.py     # Pytest suite for Auth Service (SQLite in-memory)
│   ├── Dockerfile           # Docker container specification
│   └── requirements.txt     # Python dependencies
├── user-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py          # Bearer JWT verification dependency
│   │   ├── database.py      # SQLAlchemy database engine
│   │   ├── main.py          # FastAPI profile endpoints
│   │   └── models.py        # SQLAlchemy UserProfileDB model & Pydantic schemas
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_user.py     # Pytest suite for User Service
│   ├── Dockerfile
│   └── requirements.txt
├── task-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py          # Bearer JWT verification dependency
│   │   ├── database.py      # SQLAlchemy database engine
│   │   ├── main.py          # FastAPI task management endpoints
│   │   └── models.py        # SQLAlchemy TaskDB model & Pydantic schemas
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_task.py     # Pytest suite for Task Service
│   ├── Dockerfile
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── ci.yml           # GitHub Actions CI pipeline (Pytest + Docker build)
│       └── deploy_hf.yml    # Deployment workflow with pre-deploy testing
├── docker-compose.yml       # 4-Container Docker Compose configuration
└── README.md                # Documentation & Usage Guide
```

---

## 🚀 Getting Started

### 1. Running with Docker Compose (Recommended)

To build and launch PostgreSQL and all 3 microservices concurrently:

```bash
docker compose up --build -d
```

Check container status and health checks:
```bash
docker compose ps
```

View container logs:
```bash
docker compose logs -f
```

Stop services:
```bash
docker compose down
```

---

### 2. Running & Testing Locally with Pytest

Unit tests run isolated against lightning-fast in-memory SQLite (`sqlite:///:memory:`) so you don't need a live database server running during test execution:

#### Install dependencies into local environment:
```bash
pip install -r auth-service/requirements.txt
pip install -r user-service/requirements.txt
pip install -r task-service/requirements.txt
```

#### Run All Test Suites:
```bash
(cd auth-service && PYTHONPATH=. pytest tests/ -v)
(cd user-service && PYTHONPATH=. pytest tests/ -v)
(cd task-service && PYTHONPATH=. pytest tests/ -v)
```

---

## 🧪 Testing the APIs (cURL Examples)

### Step 1: Register a New User (`auth-service` -> `auth_db`)
```bash
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "mysecretpassword"
  }'
```

### Step 2: Login to Obtain JWT Token (`auth-service`)
```bash
curl -X POST "http://localhost:8001/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "mysecretpassword"
  }'
```
*Response:*
```json
{
  "access_token": "<YOUR_JWT_TOKEN>",
  "token_type": "bearer"
}
```

### Step 3: Fetch User Profile (`user-service` -> `user_db`)
```bash
curl -X GET "http://localhost:8002/users/profile" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### Step 4: Create a Task (`task-service` -> `task_db`)
```bash
curl -X POST "http://localhost:8003/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI & Docker",
    "description": "Build microservices with PostgreSQL, Pytest, and CI/CD",
    "completed": false
  }'
```

### Step 5: Get All User Tasks (`task-service`)
```bash
curl -X GET "http://localhost:8003/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```
