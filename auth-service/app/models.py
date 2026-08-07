# Import BaseModel, Field, and ConfigDict from Pydantic for request and response validation
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
# Import SQLAlchemy Column types and Base class
from sqlalchemy import Column, Integer, String
from app.database import Base

# ── SQLALCHEMY DB MODEL ───────────────────────────────────────────────────────
class UserDB(Base):
    """
    SQLAlchemy database table model for storing user account details in auth_db.
    """
    __tablename__ = "users"

    # Primary key auto-incrementing integer user ID
    id = Column(Integer, primary_key=True, index=True)
    # Unique username string column
    username = Column(String, unique=True, index=True, nullable=False)
    # User email address column
    email = Column(String, unique=True, index=True, nullable=False)
    # Bcrypt hashed password string column
    hashed_password = Column(String, nullable=False)


# ── PYDANTIC SCHEMAS ──────────────────────────────────────────────────────────
# Model representing user registration request payload
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for account creation")
    email: str = Field(..., description="Valid email address of the user")
    password: str = Field(..., min_length=6, description="Raw account password to be hashed")

# Model representing user login request payload
class UserLogin(BaseModel):
    username: str = Field(..., description="Account username")
    password: str = Field(..., description="Account password")

# Model representing JWT Token response returned after successful authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Model representing claims extracted from a validated JWT Token
class TokenData(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

# Model representing user response data (excluding sensitive fields like hashed password)
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
