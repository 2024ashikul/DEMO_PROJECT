# Import FastAPI web framework class, HTTP status codes, and exception classes
from fastapi import FastAPI, HTTPException, status, Depends
# Import FastAPI CORS middleware to allow cross-origin request handling
from fastapi.middleware.cors import CORSMiddleware
# Import SQLAlchemy Session type
from sqlalchemy.orm import Session
# Import data models and database objects
from app.database import engine, Base, get_db
from app.models import UserRegister, UserLogin, Token, UserResponse, TokenData, UserDB
# Import authentication utility functions (hashing, JWT creation, token verification)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_from_token,
    decode_access_token
)

# Automatically create database tables on application startup if they don't exist
Base.metadata.create_all(bind=engine)

# Instantiate FastAPI application instance
app = FastAPI(
    title="Auth Service",
    description="Microservice responsible for User Registration, Authentication, and JWT Token Management",
    version="1.0.0"
)

# Add CORS middleware to enable API interaction from web clients or cross-container apps
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
    Health check endpoint used by Docker, Kubernetes, and monitoring tools to check service availability.
    """
    return {"status": "healthy", "service": "auth-service"}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """
    User registration endpoint. Validates payload, checks if user exists in database, hashes password, and saves user.
    """
    # Query database to check if username already exists
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash raw user password securely using bcrypt
    hashed_pwd = hash_password(user.password)
    
    # Construct UserDB model instance
    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    
    # Add new record to database session and commit transaction
    db.add(db_user)
    db.commit()
    # Refresh instance to retrieve generated primary key ID from database
    db.refresh(db_user)
    
    # Return UserResponse object
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint. Authenticates credentials against database and returns JWT Bearer access token.
    """
    # Look up user record by username in PostgreSQL database
    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    
    # Validate user existence and verify hashed password against input password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT access token containing subject (username) and email claims
    access_token = create_access_token(
        data={"sub": user.username, "email": user.email}
    )
    
    # Return token response payload conforming to OAuth2 Bearer standard
    return Token(access_token=access_token, token_type="bearer")

@app.post("/verify", response_model=TokenData)
def verify_token_endpoint(token: str):
    """
    Internal service endpoint to verify a JWT token string.
    """
    return decode_access_token(token)

@app.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint to retrieve current logged-in user profile using Bearer token dependency.
    """
    # Fetch full user details from database using token subject
    user = db.query(UserDB).filter(UserDB.username == current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return user
