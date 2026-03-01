from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.routers import auth, users, items


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()

    # Crear admin inicial
    from app.services.user_service import create_initial_admin
    async with AsyncSessionLocal() as db:
        await create_initial_admin(db)
        await db.commit()

    print("✅ Base de datos lista. Admin por defecto: admin / admin1234")
    yield

    # Shutdown
    print("👋 Cerrando aplicación...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## FastAPI Project 🚀

API con autenticación JWT, roles, middlewares y más.

### Features
- 🔐 Auth con JWT (registro, login, me)
- 👥 CRUD de usuarios con roles (user / admin)
- 📦 Items resource protegido
- 🛡️ Rate limiting por IP
- 📝 Logging de requests
- 🌐 CORS configurado
""",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middlewares (orden importa: se ejecutan de abajo hacia arriba) ──────────

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,
    window_seconds=60,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────

PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(items.router, prefix=PREFIX)


# ── Health check ───────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health",
    }
