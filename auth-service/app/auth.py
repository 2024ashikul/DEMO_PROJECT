# Import OS module to read environment variables (such as secret keys)
import os
# Import datetime and timedelta to calculate token expiration times
from datetime import datetime, timedelta, timezone
# Import PyJWT for encoding and decoding JSON Web Tokens
import jwt
# Import bcrypt for secure password hashing and verification
import bcrypt
# Import HTTPException and status code standards from FastAPI
from fastapi import HTTPException, status, Depends
# Import HTTPBearer security scheme to extract Bearer authorization headers
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Import TokenData model to hold decoded token payload properties
from app.models import TokenData

# Secret key used for signing JWT tokens. Default fallback provided for development.
SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-demo-microservices")
# Algorithm used for signing JWT tokens (HMAC SHA-256)
ALGORITHM: str = "HS256"
# Expiration duration for access tokens in minutes (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Initialize HTTPBearer security scheme for FastAPI dependency injection
security = HTTPBearer()

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt with salt.
    Truncates password to 72 bytes max to adhere to bcrypt standard limit.
    """
    # Convert string to UTF-8 bytes and slice to 72 bytes maximum
    pwd_bytes = password.encode('utf-8')[:72]
    # Generate random bcrypt salt
    salt = bcrypt.gensalt()
    # Hash password bytes with salt and return decoded UTF-8 string
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash string.
    """
    # Convert plain password string to UTF-8 bytes (sliced to 72 bytes)
    pwd_bytes = plain_password.encode('utf-8')[:72]
    # Convert stored hashed password string to UTF-8 bytes
    hashed_bytes = hashed_password.encode('utf-8')
    # Compare plain password bytes against hash returning boolean result
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a signed JWT access token containing custom claims and expiration timestamp.
    """
    # Create a copy of input payload dictionary to prevent modifying caller's data
    to_encode = data.copy()
    
    # Calculate token expiration timestamp
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Set standard 'exp' (expiration time) claim in payload
    to_encode.update({"exp": expire})
    
    # Encode payload into signed JWT string using SECRET_KEY and HS256 algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Return JWT token string
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Decodes and validates a JWT access token string.
    Raises HTTPException if expired or invalid.
    """
    try:
        # Decode token payload using SECRET_KEY and HS256 algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract subject claim (username)
        username: str = payload.get("sub")
        # Extract email claim
        email: str = payload.get("email")
        
        # Validate that username subject exists
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return TokenData object containing validated claims
        return TokenData(username=username, email=email)
        
    except jwt.ExpiredSignatureError:
        # Raised when current timestamp exceeds token 'exp' claim
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        # Raised when token signature is invalid or token structure is corrupted
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    FastAPI dependency that extracts Bearer token from HTTP Authorization header
    and returns verified TokenData claims.
    """
    # Extract token string from Authorization header credentials
    token = credentials.credentials
    # Decode and validate token using utility function
    return decode_access_token(token)
