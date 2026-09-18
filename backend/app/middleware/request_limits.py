"""
HealthConnect AI - Request limits middleware.
Rate limiting (in-memory) + body size limit.
"""
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging_config import get_logger

logger = get_logger(__name__)

MAX_BODY_BYTES = 8 * 1024            # 8 KB JSON payload max
RATE_WINDOW_SECONDS = 60
RATE_MAX_REQUESTS = 60               # 60 chat messages / min / IP
CHAT_RATE_MAX_REQUESTS = 20          # stricter for /chat/message


class RequestLimitsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque] = defaultdict(deque)

    def _rate_limited(self, key: str, limit: int) -> bool:
        now = time.time()
        q = self._hits[key]
        while q and now - q[0] > RATE_WINDOW_SECONDS:
            q.popleft()
        if len(q) >= limit:
            return True
        q.append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Body size guard (best-effort — check Content-Length header)
        cl = request.headers.get("content-length")
        if cl and int(cl) > MAX_BODY_BYTES:
            logger.warning(f"Rejected oversized body from {ip}: {cl} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body too large",
            )

        # Streaming endpoints are long-lived — skip rate limiting
        if "/chat/message/stream" in path or "/ws/" in path:
            return await call_next(request)

        # Rate limit (regular endpoints)
        if "/chat/message" in path:
            limit = CHAT_RATE_MAX_REQUESTS
        else:
            limit = RATE_MAX_REQUESTS
        if self._rate_limited(ip, limit):
            logger.warning(f"Rate limit exceeded for {ip} on {path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
            )

        return await call_next(request)
