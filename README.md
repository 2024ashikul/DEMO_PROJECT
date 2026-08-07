---
title: FastAPI Microservices Ecosystem
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# FastAPI 3-Service Microservices Ecosystem

A complete, production-ready microservices system built with **FastAPI**, **PostgreSQL**, **SQLAlchemy ORM**, **Docker**, **Docker Compose**, **Pytest**, and **GitHub Actions CI/CD** (with native support for **Hugging Face Spaces**).

---

## 🏛️ System Architecture Overview

The project supports two deployment modes out-of-the-box:

### Mode A: Multi-Container Docker Compose (Local / VPS / Cloud Server)
Each microservice runs in its own container, backed by a dedicated PostgreSQL container with isolated databases (`auth_db`, `user_db`, `task_db`).

| Service | Container Name | Port | Description |
| :--- | :--- | :--- | :--- |
| **`postgres-db`** | `postgres-db` | `5432` | Runs PostgreSQL 16 with `auth_db`, `user_db`, and `task_db` |
| **`auth-service`** | `auth-service` | `8001` | User registration, password hashing (bcrypt), JWT generation & verification |
| **`user-service`** | `user-service` | `8002` | User profile retrieval and profile customization |
| **`task-service`** | `task-service` | `8003` | Task/Todo management (CRUD operations) |

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

### Mode B: Hugging Face Spaces Deployment (Single Container Gateway)
Hugging Face Spaces runs a single container listening on port `7860`. The root [Dockerfile](file:///Users/macbook/Documents/demo_project/DEMO_PROJECT/Dockerfile) uses **Supervisord** and **Nginx** to run all 3 microservices behind a unified gateway:

```
                    +------------------------------------+
                    |    Hugging Face Space (Port 7860)  |
                    |                                    |
                    |     +------------------------+     |
                    |     |     Nginx Gateway      |     |
                    |     |      (Port 7860)       |     |
                    |     +-----------+------------+     |
                    |                 |                  |
            +-------------------------+-------------------------+
            |                         |                         |
    +-------v-------+         +-------v-------+         +-------v-------+
    | auth-service  |         | user-service  |         | task-service  |
    |  (Port 8001)  |         |  (Port 8002)  |         |  (Port 8003)  |
    +---------------+         +---------------+         +---------------+
```

---

## 📂 Project Structure

```
.
├── Dockerfile               # Root Dockerfile for Hugging Face Spaces (Port 7860)
├── supervisord.conf         # Supervisord process manager configuration for HF Spaces
├── nginx.conf               # Nginx reverse proxy routing /auth, /user, /task on port 7860
├── docker/
│   └── init-dbs.sql         # SQL script initializing auth_db, user_db, task_db in Postgres
├── auth-service/
│   ├── app/
│   │   ├── auth.py          # Hashing (Bcrypt) & JWT creation/decoding
│   │   ├── database.py      # SQLAlchemy engine
│   │   ├── main.py          # FastAPI application & auth endpoints
│   │   └── models.py        # UserDB model & Pydantic schemas
│   └── tests/
│       └── test_auth.py     # Pytest suite for Auth Service (SQLite in-memory)
├── user-service/
│   ├── app/
│   │   ├── auth.py          # Bearer JWT verification dependency
│   │   ├── database.py      # SQLAlchemy engine
│   │   ├── main.py          # FastAPI profile endpoints
│   │   └── models.py        # UserProfileDB model & Pydantic schemas
│   └── tests/
│       └── test_user.py     # Pytest suite for User Service
├── task-service/
│   ├── app/
│   │   ├── auth.py          # Bearer JWT verification dependency
│   │   ├── database.py      # SQLAlchemy engine
│   │   ├── main.py          # FastAPI task management endpoints
│   │   └── models.py        # TaskDB model & Pydantic schemas
│   └── tests/
│       └── test_task.py     # Pytest suite for Task Service
├── .github/
│   └── workflows/
│       ├── ci.yml           # GitHub Actions CI pipeline (Pytest + Docker build)
│       └── deploy_hf.yml    # Hugging Face deployment pipeline
├── docker-compose.yml       # 4-Container Docker Compose configuration
└── README.md                # Documentation & Usage Guide with HF YAML Frontmatter
```

---

## 🚀 How to Run & Deploy

### Option 1: Deploying to Hugging Face Spaces (Automatic via CI/CD)
1. Push your repository to GitHub `main` branch.
2. Ensure secret `HF_TOKEN` is set in your GitHub Repository Secrets.
3. The `.github/workflows/deploy_hf.yml` action will run all Pytest suites and push the code directly to Hugging Face.
4. Hugging Face Spaces will build the root `Dockerfile` and expose all microservices on port `7860`:
   - Landing Dashboard: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE/`
   - Auth Service: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE/auth/docs`
   - User Service: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE/user/docs`
   - Task Service: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE/task/docs`

---

### Option 2: Running locally with Docker Compose

```bash
docker compose up --build -d
```

Check running status:
```bash
docker compose ps
```

---

### Option 3: Running Unit Tests locally with Pytest

```bash
source .venv/bin/activate
(cd auth-service && PYTHONPATH=. pytest tests/ -v)
(cd user-service && PYTHONPATH=. pytest tests/ -v)
(cd task-service && PYTHONPATH=. pytest tests/ -v)
```

---

## 🧪 cURL Testing Commands (Hugging Face Spaces vs Docker Compose)

### 1. Register User
- **HF Spaces:** `curl -X POST "https://<HF_SPACE_URL>/auth/register"`
- **Docker Compose:** `curl -X POST "http://localhost:8001/register"`

### 2. Login to Obtain Token
- **HF Spaces:** `curl -X POST "https://<HF_SPACE_URL>/auth/token"`
- **Docker Compose:** `curl -X POST "http://localhost:8001/token"`

### 3. Get Profile
- **HF Spaces:** `curl -X GET "https://<HF_SPACE_URL>/user/users/profile" -H "Authorization: Bearer <TOKEN>"`
- **Docker Compose:** `curl -X GET "http://localhost:8002/users/profile" -H "Authorization: Bearer <TOKEN>"`

### 4. Create Task
- **HF Spaces:** `curl -X POST "https://<HF_SPACE_URL>/task/tasks" -H "Authorization: Bearer <TOKEN>"`
- **Docker Compose:** `curl -X POST "http://localhost:8003/tasks" -H "Authorization: Bearer <TOKEN>"`
