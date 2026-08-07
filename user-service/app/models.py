# Import Pydantic BaseModel, Field, and ConfigDict for payload schemas
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
# Import SQLAlchemy Column types and Base class
from sqlalchemy import Column, Integer, String
from app.database import Base

# ── SQLALCHEMY DB MODEL ───────────────────────────────────────────────────────
class UserProfileDB(Base):
    """
    SQLAlchemy database table model for storing user profiles in user_db.
    """
    __tablename__ = "user_profiles"

    # Primary key auto-incrementing integer ID
    id = Column(Integer, primary_key=True, index=True)
    # Unique username string matching authentication identity
    username = Column(String, unique=True, index=True, nullable=False)
    # User email address
    email = Column(String, nullable=True)
    # Full name string
    full_name = Column(String, nullable=False, default="")
    # Biography text string
    bio = Column(String, nullable=False, default="")
    # Location string
    location = Column(String, nullable=False, default="")


# ── PYDANTIC SCHEMAS ──────────────────────────────────────────────────────────
class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: Optional[str] = None
    full_name: str
    bio: str
    location: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, description="Updated full name of user")
    bio: Optional[str] = Field(None, description="Updated biography")
    location: Optional[str] = Field(None, description="Updated location")
