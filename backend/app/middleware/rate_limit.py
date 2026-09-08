"""
HealthConnect AI - Rate Limiting Middleware
============================================
Rate limiting middleware using Redis for distributed rate limiting.

Features:
- IP-based rate limiting
- User-based rate limiting
- Token bucket algorithm
- Custom rate limits per endpoint
- Rate limit headers
"""

import time
import hashlib
from typing import Dict, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    
    Uses sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limits = {
            "default": {
                "requests": settings.rate_limit.REQUESTS,
                "period": settings.rate_limit.PERIOD,
            },
            "/chat": {
                "requests": 50,
                "period": 60,
            },
            "/appointment": {
                "requests": 20,
                "period": 60,
            },
            "/auth/login": {
                "requests": 5,
                "period": 60,
            },
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        if not settings.rate_limit.ENABLED:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Get rate limit for endpoint
        rate_limit = self._get_rate_limit(request.url.path)
        
        # Check rate limit
        is_allowed, retry_after = await self._check_rate_limit(
            client_id,
            rate_limit["requests"],
            rate_limit["period"],
        )
        
        if not is_allowed:
            from app.core.exceptions import RateLimitExceededError
            raise RateLimitExceededError(
                retry_after=retry_after,
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(
            client_id,
            rate_limit["requests"],
            rate_limit["period"],
        )
        response.headers["X-RateLimit-Limit"] = str(rate_limit["requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + rate_limit["period"]))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier.
        Priority: User ID > IP Address
        """
        # Try to get user ID from request
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _get_rate_limit(self, path: str) -> Dict:
        """Get rate limit for endpoint"""
        for pattern, limit in self.rate_limits.items():
            if pattern in path:
                return limit
        return self.rate_limits["default"]
    
    async def _check_rate_limit(
        self,
        client_id: str,
        max_requests: int,
        period: int,
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if client has exceeded rate limit.
        Uses sliding window algorithm.
        
        Returns:
            Tuple[bool, Optional[int]]: (is_allowed, retry_after_seconds)
        """
        if not self.redis_client:
            # Fallback to in-memory rate limiting
            return self._check_rate_limit_memory(client_id, max_requests, period)
        
        current_time = time.time()
        window_start = current_time - period
        
        # Redis key for this client's requests
        redis_key = f"rate:{client_id}"
        
        try:
            # Remove old requests
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current requests
            request_count = self.redis_client.zcard(redis_key)
            
            if request_count >= max_requests:
                # Get oldest request for retry-after calculation
                oldest = self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1] + period - current_time)
                    return False, max(retry_after, 1)
                return False, period
            
            # Add current request
            self.redis_client.zadd(redis_key, {str(current_time): current_time})
            self.redis_client.expire(redis_key, period)
            
            return True, None
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, None  # Fail open on error
    
    def _check_rate_limit_memory(
        self,
        client_id: str,
        max_requests: int,
        period: int,
    ) -> Tuple[bool, Optional[int]]:
        """In-memory rate limiting fallback"""
        if not hasattr(self, "_memory_store"):
            self._memory_store = {}
        
        current_time = time.time()
        window_start = current_time - period
        
        # Clean old requests
        if client_id in self._memory_store:
            self._memory_store[client_id] = [
                ts for ts in self._memory_store[client_id] if ts > window_start
            ]
        else:
            self._memory_store[client_id] = []
        
        # Check rate limit
        if len(self._memory_store[client_id]) >= max_requests:
            retry_after = int(self._memory_store[client_id][0] + period - current_time)
            return False, max(retry_after, 1)
        
        # Add request
        self._memory_store[client_id].append(current_time)
        
        return True, None
    
    async def _get_remaining_requests(
        self,
        client_id: str,
        max_requests: int,
        period: int,
    ) -> int:
        """Get remaining requests for client"""
        if not self.redis_client:
            return max_requests
        
        current_time = time.time()
        window_start = current_time - period
        redis_key = f"rate:{client_id}"
        
        try:
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            request_count = self.redis_client.zcard(redis_key)
            return max(0, max_requests - request_count)
        except Exception:
            return max_requests