import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Por esto:
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Registra cada request con método, path, status code y tiempo de respuesta."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} "
            f"[{process_time:.2f}ms] "
            f"| IP: {request.client.host if request.client else 'unknown'}"
        )

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
