# Import OS module to retrieve environment configuration
import os
# Import PyJWT for decoding JWT access tokens
import jwt
# Import FastAPI HTTP exceptions and dependency injection utilities
from fastapi import HTTPException, status, Depends
# Import HTTPBearer security scheme
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Import Pydantic model for type checking user claims
from pydantic import BaseModel
from typing import Optional

# Shared secret key matching auth-service and user-service
SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-demo-microservices")
# Signature algorithm
ALGORITHM: str = "HS256"

# Claims data container model
class UserClaim(BaseModel):
    username: str
    email: Optional[str] = None

# Initialize HTTPBearer security scheme
security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserClaim:
    """
    FastAPI dependency that extracts and validates incoming Bearer JWT tokens.
    Returns UserClaim object containing token subject (username).
    """
    # Extract Bearer token string
    token = credentials.credentials
    
    try:
        # Decode token payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username claim from token subject ('sub')
        username: str = payload.get("sub")
        email: str = payload.get("email")
        
        # Ensure subject claim is present
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Return claims object
        return UserClaim(username=username, email=email)
        
    except jwt.ExpiredSignatureError:
        # Token expiration exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        # Signature mismatch or bad formatting exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
