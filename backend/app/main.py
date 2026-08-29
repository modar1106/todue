"""
FastAPI Application Entry Point.
Configures CORS, includes routers, and sets up exception handlers.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.auth import router as auth_router
from app.routes.todos import router as todos_router


def create_app() -> FastAPI:
    """Application factory pattern."""
    settings = get_settings()

    app = FastAPI(
        title="Todue   API",
        description=(
            "REST API for a Todue -inspired Todo List application. "
            "Features multi-user authentication, CRUD operations, "
            "filtering, sorting, pagination, and bulk data generation."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS Middleware ──────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # ── Include Routers ─────────────────────────────────────
    app.include_router(auth_router)
    app.include_router(todos_router)

    # ── Global Exception Handler ────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Catch-all handler to prevent stack traces leaking to clients."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal Server Error",
                "detail": str(exc) if settings.APP_DEBUG else "An unexpected error occurred.",
            },
        )

    # ── Health Check ────────────────────────────────────────
    @app.get("/", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "Todue   API",
            "version": "1.0.0",
        }

    @app.get("/api/health", tags=["Health"])
    async def api_health():
        """API health check endpoint."""
        return {
            "status": "ok",
            "message": "API is running.",
        }

    return app


# Create the app instance
app = create_app()
