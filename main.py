"""
Trade Opportunities API - FastAPI Application

A production-ready FastAPI service for analyzing Indian market data
and returning trade opportunity insights for given sectors.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from api.routes import router
from api.auth_routes import auth_router
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger()

# Create FastAPI app
app = FastAPI(
    title="Trade Opportunities API",
    description="""
    A FastAPI service for analyzing Indian market data and generating 
    trade opportunity insights as structured Markdown reports.
    
    ## Features
    
    * **JWT Authentication**: Secure token-based authentication
    * **Rate Limiting**: Per-user rate limiting to prevent abuse
    * **AI-Powered Analysis**: Uses Google Gemini API for market analysis
    * **Market Data Integration**: Fetches recent market news and data
    * **Structured Reports**: Returns well-formatted Markdown reports
    
    ## Authentication
    
    Use the `/auth/login` endpoint to get a JWT token, then include it in 
    the Authorization header as: `Bearer <token>`
    
    ## Rate Limits
    
    Default: 10 requests per minute per user
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(auth_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Trade Opportunities API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    # Check if Gemini API key is configured
    gemini_key = os.getenv("GEMINI_API_KEY")
    status = "healthy" if gemini_key else "degraded"
    
    return {
        "status": status,
        "service": "Trade Opportunities API",
        "gemini_configured": bool(gemini_key),
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
        },
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Trade Opportunities API starting up...")
    
    # Validate required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.warning(
            "GEMINI_API_KEY not found in environment variables. "
            "AI service will not be available until configured."
        )
    else:
        logger.info("GEMINI_API_KEY configured")
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Trade Opportunities API shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

