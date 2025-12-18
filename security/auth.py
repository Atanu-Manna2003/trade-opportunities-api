"""JWT authentication implementation."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

from utils.logger import setup_logger

logger = setup_logger()

# JWT Configuration
# Use environment variable if set, otherwise generate a secure random key
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HTTP Bearer token security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token (e.g., {"sub": username})
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"Token created for user: {data.get('sub', 'unknown')}")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token verified successfully for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        logger.debug(f"Using SECRET_KEY (first 10 chars): {SECRET_KEY[:10]}...")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    logger.debug(f"Verifying token (first 20 chars): {token[:20]}...")
    payload = verify_token(token)
    
    if payload is None:
        logger.warning("Authentication failed: Invalid token (token verification returned None)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials. Token may have expired or server was restarted. Please get a new token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id", username)
    
    if username is None:
        logger.warning("Authentication failed: Missing username in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"User authenticated: {username}")
    return {"username": username, "user_id": user_id}


def authenticate_user(username: str, password: str) -> bool:
    """
    Simple user authentication (for demo purposes).
    In production, this should check against a database.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        True if authenticated, False otherwise
    """
    # Simple demo authentication - accept any credentials
    # In production, this should verify against a user database
    return bool(username and password)

