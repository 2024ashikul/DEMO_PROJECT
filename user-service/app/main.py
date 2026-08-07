# Import OS module to read environment configuration
import os
# Import FastAPI class, HTTP exceptions, status codes, and dependency injection
from fastapi import FastAPI, HTTPException, status, Depends
# Import CORS middleware for microservice communication
from fastapi.middleware.cors import CORSMiddleware
# Import SQLAlchemy Session type
from sqlalchemy.orm import Session
# Import database objects and models
from app.database import engine, Base, get_db
from app.models import UserProfile, ProfileUpdateRequest, UserProfileDB
# Import JWT verification dependency and UserClaim model
from app.auth import verify_jwt_token, UserClaim

# Automatically create user_profiles table if it does not exist
Base.metadata.create_all(bind=engine)

# Read root_path from environment variable for Nginx proxy compatibility (e.g. /user)
root_path = os.getenv("ROOT_PATH", "")

# Instantiate FastAPI user service app instance
app = FastAPI(
    title="User Service",
    description="Microservice responsible for User Profile Management and User Metadata",
    version="1.0.0",
    root_path=root_path
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
    Health check endpoint for user-service monitoring.
    """
    return {"status": "healthy", "service": "user-service"}

@app.get("/users/profile", response_model=UserProfile)
def get_user_profile(
    user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Fetch user profile data from user_db based on authenticated token identity.
    """
    # Retrieve profile record from database
    profile = db.query(UserProfileDB).filter(UserProfileDB.username == user.username).first()
    
    # If profile does not exist yet, create default profile record in database
    if not profile:
        profile = UserProfileDB(
            username=user.username,
            email=user.email,
            full_name=user.username.title(),
            bio="Software Developer & Microservices Enthusiast",
            location="Global / Remote"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile

@app.put("/users/profile", response_model=UserProfile)
def update_user_profile(
    update_data: ProfileUpdateRequest,
    user: UserClaim = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint: Update profile bio, full name, or location in database for authenticated user.
    """
    # Query database for existing profile record
    profile = db.query(UserProfileDB).filter(UserProfileDB.username == user.username).first()
    
    # Create profile if not present
    if not profile:
        profile = UserProfileDB(
            username=user.username,
            email=user.email,
            full_name=user.username.title(),
            bio="Software Developer & Microservices Enthusiast",
            location="Global / Remote"
        )
        db.add(profile)

    # Update non-null input fields
    if update_data.full_name is not None:
        profile.full_name = update_data.full_name
    if update_data.bio is not None:
        profile.bio = update_data.bio
    if update_data.location is not None:
        profile.location = update_data.location

    # Save changes to database transaction
    db.commit()
    db.refresh(profile)

    return profile
