"""Main API routes for sector analysis."""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from models.schemas import AnalyzeResponse
from security.auth import get_current_user
from security.rate_limiter import rate_limiter
from services.search_service import SearchService
from services.ai_service import AIService
from utils.logger import setup_logger
from utils.validators import validate_sector, normalize_sector

logger = setup_logger()

router = APIRouter()

# Initialize services
search_service = SearchService()
ai_service = None  # Will be initialized on first request


def get_ai_service() -> AIService:
    """Lazy initialization of AI service."""
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError as e:
            logger.error(f"Failed to initialize AI service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service not available. Please check GEMINI_API_KEY configuration.",
            )
    return ai_service


@router.get(
    "/analyze/{sector}",
    response_model=AnalyzeResponse,
    summary="Analyze trade opportunities for a sector",
    description="Get a structured Markdown report analyzing trade opportunities for a given sector in the Indian market.",
)
async def analyze_sector(
    sector: str,
    current_user: dict = Depends(get_current_user),
) -> AnalyzeResponse:
    """
    Analyze trade opportunities for a given sector.
    
    This endpoint:
    1. Validates the sector input
    2. Checks rate limits for the user
    3. Fetches recent market data
    4. Generates AI-powered analysis report
    5. Returns structured Markdown report
    
    Args:
        sector: Sector name (e.g., pharmaceuticals, technology)
        current_user: Authenticated user (from JWT)
        
    Returns:
        AnalyzeResponse with Markdown report
        
    Raises:
        HTTPException: For validation, rate limit, or service errors
    """
    user_id = current_user.get("user_id", current_user.get("username", "unknown"))
    
    logger.info(f"Analysis request for sector '{sector}' from user: {user_id}")
    
    # 1. Validate sector input
    normalized_sector = normalize_sector(sector)
    if not validate_sector(normalized_sector, strict=False):
        logger.warning(f"Invalid sector format: {sector}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sector format. Sector must contain only letters, numbers, spaces, and hyphens.",
        )
    
    # 2. Check rate limiting
    is_allowed, remaining, reset_after = await rate_limiter.is_allowed(user_id)
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again after {reset_after} seconds.",
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset-After": str(reset_after)},
        )
    
    try:
        # 3. Fetch market data
        logger.info(f"Fetching market data for sector: {normalized_sector}")
        market_data = await search_service.search_market_data(normalized_sector, max_results=10)
        
        # 4. Generate AI report
        logger.info(f"Generating AI report for sector: {normalized_sector}")
        ai_service = get_ai_service()
        report = await ai_service.generate_market_report(normalized_sector, market_data)
        
        # 5. Return response
        logger.info(f"Analysis complete for sector: {normalized_sector}")
        return AnalyzeResponse(
            sector=normalized_sector,
            report=report,
            generated_at=datetime.now().isoformat(),
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error analyzing sector {normalized_sector}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the sector: {str(e)}",
        )


@router.get(
    "/rate-limit-info",
    summary="Get rate limit information",
    description="Get current rate limit status for the authenticated user.",
)
async def get_rate_limit_info(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get rate limit information for the current user.
    
    Args:
        current_user: Authenticated user (from JWT)
        
    Returns:
        Dictionary with rate limit information
    """
    user_id = current_user.get("user_id", current_user.get("username", "unknown"))
    info = await rate_limiter.get_rate_limit_info(user_id)
    return info

