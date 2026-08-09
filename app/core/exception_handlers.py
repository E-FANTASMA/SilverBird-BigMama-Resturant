from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AppException,
    ConflictException,
    ExternalServiceException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.logging import get_logger, log_event

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    exception_map = {
        NotFoundException: 404,
        UnauthorizedException: 401,
        ForbiddenException: 403,
        ConflictException: 409,
        ValidationException: 422,
        ExternalServiceException: 502,
    }

    for exc_type, status_code in exception_map.items():
        app.add_exception_handler(exc_type, _handler(status_code))

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return _json_error(request, 400, str(exc), "app_error")

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _json_error(request, 422, "Request validation failed", "request_validation_error", errors=exc.errors())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _json_error(request, exc.status_code, str(exc.detail), "http_error")

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return _json_error(request, 500, "A database error occurred", "database_error", internal_error=str(exc))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return _json_error(request, 500, "Internal server error", "unexpected_error", internal_error=str(exc))


def _handler(status_code: int):
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return _json_error(request, status_code, str(exc), exc.__class__.__name__)

    return handler


def _json_error(request: Request, status_code: int, detail: str, code: str, **extra) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    log_event(
        logger,
        "http_error",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        status_code=status_code,
        code=code,
        detail=detail,
        **extra,
    )
    payload = {
        "detail": detail,
        "code": code,
        "request_id": request_id,
    }
    if "errors" in extra:
        payload["errors"] = extra["errors"]
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))
