from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.application.services.auth_service import AuthService
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.domain.enums import RoleName
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.session import SessionLocal, engine
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    async def ensure_bootstrap_data() -> None:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as session:
            existing = {role.name for role in session.query(RoleModel).all()}
            for role_name in RoleName:
                if role_name.value not in existing:
                    session.add(RoleModel(name=role_name.value, description=f"{role_name.value.title()} role"))
            session.commit()
            AuthService(session).seed_initial_admin()

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
