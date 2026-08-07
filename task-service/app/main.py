# Import FastAPI class, HTTP status codes, exceptions, and dependency injection
from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from fastapi.middleware.cors import CORSMiddleware
# Import SQLAlchemy Session type
from sqlalchemy.orm import Session
# Import database configuration and models
from app.database import engine, Base, get_db
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskDB
# Import JWT verification dependency and user claim model
from app.auth import verify_jwt_token, UserClaim

# Create database tables automatically if missing
Base.metadata.create_all(bind=engine)

# Instantiate FastAPI application instance for task-service
app = FastAPI(
    title="Task Service",
    description="Microservice responsible for Managing User Tasks, Todos, and Business Logic",
    version="1.0.0"
)

# Enable CORS for cross-service calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint for task-service monitoring.
    """
    return {"status": "healthy", "service": "task-service"}

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Create a new task owned by the authenticated user in task_db.
    """
    # Create TaskDB model instance
    db_task = TaskDB(
        owner_username=current_user.username,
        title=task_in.title,
        description=task_in.description,
        completed=task_in.completed
    )
    
    # Save task to PostgreSQL database
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@app.get("/tasks", response_model=List[TaskResponse])
def get_user_tasks(
    current_user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Retrieve all tasks owned by the authenticated user from task_db.
    """
    # Query database where owner_username matches authenticated user
    user_tasks = db.query(TaskDB).filter(TaskDB.owner_username == current_user.username).all()
    return user_tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    current_user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Retrieve a specific task by task ID owned by authenticated user.
    """
    # Look up task in database
    task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_username == current_user.username).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Update title, description, or completion status of an existing user task in database.
    """
    task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_username == current_user.username).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed

    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Delete a specific task by task ID from database.
    """
    task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner_username == current_user.username).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    db.delete(task)
    db.commit()
    
    return None
