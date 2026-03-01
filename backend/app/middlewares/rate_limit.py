import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiter simple basado en IP.
    Por defecto: 60 requests por minuto por IP.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Limpiar requests fuera de la ventana de tiempo
        self._requests[client_ip] = [
            req_time
            for req_time in self._requests[client_ip]
            if now - req_time < self.window_seconds
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Demasiadas solicitudes. Máximo {self.max_requests} por {self.window_seconds}s."
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        self._requests[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(self._requests[client_ip])
        )
        return response
