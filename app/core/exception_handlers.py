from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


def register_exception_handlers(app: FastAPI) -> None:
    exception_map = {
        NotFoundException: 404,
        UnauthorizedException: 401,
        ForbiddenException: 403,
        ConflictException: 409,
        ValidationException: 422,
    }

    for exc_type, status_code in exception_map.items():
        app.add_exception_handler(exc_type, _handler(status_code))

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})


def _handler(status_code: int):
    async def handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return handler
