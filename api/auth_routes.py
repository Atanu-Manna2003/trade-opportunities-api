"""Authentication routes for JWT token generation."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.schemas import Token
from security.auth import create_access_token, authenticate_user
from utils.logger import setup_logger

logger = setup_logger()

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# HTTP Basic Auth for login endpoint
security_basic = HTTPBasic()


@auth_router.post("/login", response_model=Token, summary="Login and get JWT token")
async def login(credentials: HTTPBasicCredentials = Depends(security_basic)) -> Token:
    """
    Authenticate user and return JWT access token.
    
    For demo purposes, accepts any username/password combination.
    In production, this should verify credentials against a user database.
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        Token with access_token and token_type
        
    Raises:
        HTTPException: If authentication fails
    """
    username = credentials.username
    password = credentials.password
    
    logger.info(f"Login attempt for user: {username}")
    
    # Authenticate user (demo: accepts any credentials)
    if not authenticate_user(username, password):
        logger.warning(f"Authentication failed for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": username, "user_id": username})
    
    logger.info(f"Login successful for user: {username}")
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/token", response_model=Token, summary="Generate token from credentials")
async def create_token(credentials: HTTPBasicCredentials = Depends(security_basic)) -> Token:
    """
    Alternative endpoint for token generation (same as /login).
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        Token with access_token and token_type
    """
    return await login(credentials)

