"""In-memory rate limiter implementation."""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import asyncio

from utils.logger import setup_logger

logger = setup_logger()


class RateLimiter:
    """
    In-memory rate limiter using token bucket algorithm.
    Thread-safe using asyncio locks.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per user: {user_id: [timestamp1, timestamp2, ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
        logger.info(f"Rate limiter initialized: {max_requests} requests per {window_seconds} seconds")
    
    async def is_allowed(self, user_id: str) -> Tuple[bool, int, int]:
        """
        Check if a request is allowed for the given user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_after_seconds)
        """
        async with self._lock:
            now = datetime.now()
            cutoff_time = now - timedelta(seconds=self.window_seconds)
            
            # Clean up old requests outside the time window
            user_requests = self._requests[user_id]
            user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
            
            # Check if limit exceeded
            request_count = len(user_requests)
            remaining = max(0, self.max_requests - request_count)
            is_allowed = request_count < self.max_requests
            
            if is_allowed:
                # Add current request timestamp
                user_requests.append(now)
                logger.debug(f"Rate limit check passed for user {user_id}: {remaining - 1} requests remaining")
            else:
                # Calculate reset time (oldest request + window)
                if user_requests:
                    oldest_request = min(user_requests)
                    reset_time = oldest_request + timedelta(seconds=self.window_seconds)
                    reset_after = max(0, int((reset_time - now).total_seconds()))
                else:
                    reset_after = self.window_seconds
                
                logger.warning(f"Rate limit exceeded for user {user_id}. Resets in {reset_after} seconds")
            
            return is_allowed, remaining, self.window_seconds
    
    async def get_rate_limit_info(self, user_id: str) -> Dict[str, int]:
        """
        Get rate limit information for a user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary with rate limit info
        """
        async with self._lock:
            now = datetime.now()
            cutoff_time = now - timedelta(seconds=self.window_seconds)
            
            user_requests = self._requests[user_id]
            user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
            
            request_count = len(user_requests)
            remaining = max(0, self.max_requests - request_count)
            
            return {
                "limit": self.max_requests,
                "remaining": remaining,
                "reset_after": self.window_seconds,
            }


# Global rate limiter instance
# Default: 10 requests per minute per user
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

