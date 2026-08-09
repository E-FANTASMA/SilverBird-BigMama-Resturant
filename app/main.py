from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    docs_path = "/docs"
    health_path = "/health"
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.app_version,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=docs_path,
        redoc_url="/redoc",
    )
    app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        return {
            "message": f"{settings.app_name} is running.",
            "docs_url": docs_path,
            "health_url": health_path,
            "api_base": settings.api_v1_prefix,
        }

    @app.get(health_path, tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
