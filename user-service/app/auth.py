# Import OS module to read environment variable configuration
import os
# Import PyJWT for decoding and verifying JWT tokens
import jwt
# Import FastAPI exception and dependency injection tools
from fastapi import HTTPException, status, Depends
# Import HTTPBearer security scheme to extract token from headers
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Import Pydantic model for holding extracted token claims
from pydantic import BaseModel
from typing import Optional

# Secret key matching the auth-service signing key
SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-demo-microservices")
# Signing algorithm standard
ALGORITHM: str = "HS256"

# Pydantic model representing decoded claims
class UserClaim(BaseModel):
    username: str
    email: Optional[str] = None

# Initialize HTTPBearer security scheme
security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserClaim:
    """
    FastAPI dependency function that validates incoming Bearer JWT tokens.
    Extracts claims and returns UserClaim object.
    """
    # Extract token string from HTTP header
    token = credentials.credentials
    
    try:
        # Decode token using shared secret key and HS256 algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username claim from token subject
        username: str = payload.get("sub")
        # Extract email claim
        email: str = payload.get("email")
        
        # Ensure username exists in payload
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Return validated UserClaim model
        return UserClaim(username=username, email=email)
        
    except jwt.ExpiredSignatureError:
        # Token timestamp expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        # Invalid signature or malformed token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
