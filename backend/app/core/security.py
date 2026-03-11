"""Security utilities: rate limiting, file validation, input sanitization."""

import re
import os
import logging
from collections import defaultdict
from time import time
from fastapi import HTTPException, Request, UploadFile, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter (in-memory, suitable for single-instance deployments)
# ---------------------------------------------------------------------------
class RateLimiter:
    """Simple sliding-window rate limiter keyed by client IP."""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, client_ip: str) -> None:
        settings = get_settings()
        now = time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        max_requests = settings.RATE_LIMIT_REQUESTS

        # Prune expired timestamps
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > now - window
        ]

        if len(self._requests[client_ip]) >= max_requests:
            logger.warning("Rate limit exceeded for %s", client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        self._requests[client_ip].append(now)


rate_limiter = RateLimiter()


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------
async def validate_upload_file(file: UploadFile) -> bytes:
    """Validate uploaded file type and size, return raw bytes."""
    settings = get_settings()

    # Check extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Accepted: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read and check size
    contents = await file.read()
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    return contents


# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def sanitize_email(email: str) -> str:
    """Validate and sanitize an email address."""
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address.",
        )
    return email


def get_client_ip(request: Request) -> str:
    """Extract client IP from the request, respecting X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
