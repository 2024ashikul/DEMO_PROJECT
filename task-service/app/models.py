# Import Pydantic BaseModel, Field, and ConfigDict for task payload schemas
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
# Import SQLAlchemy Column types and Base class
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

# ── SQLALCHEMY DB MODEL ───────────────────────────────────────────────────────
class TaskDB(Base):
    """
    SQLAlchemy database table model for storing tasks in task_db.
    """
    __tablename__ = "tasks"

    # Primary key auto-incrementing integer task ID
    id = Column(Integer, primary_key=True, index=True)
    # Owner username string mapping to token subject
    owner_username = Column(String, index=True, nullable=False)
    # Task title string
    title = Column(String, nullable=False)
    # Task description text
    description = Column(String, nullable=True)
    # Task completion status boolean flag
    completed = Column(Boolean, default=False, nullable=False)


# ── PYDANTIC SCHEMAS ──────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Short title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    completed: bool = Field(default=False, description="Task completion status")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    completed: Optional[bool] = Field(None)

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_username: str
    title: str
    description: Optional[str] = None
    completed: bool
