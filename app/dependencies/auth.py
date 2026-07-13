from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.domain.enums import RoleName
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.session import get_db_session

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db_session),
):
    if not credentials:
        raise UnauthorizedException("Authentication credentials were not provided")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedException(str(exc)) from exc
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")
    return UserRepository(session).get(UUID(user_id))


def require_roles(*roles: RoleName):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.role.name not in {role.value for role in roles}:
            raise ForbiddenException("You do not have access to this resource")
        return current_user

    return dependency
