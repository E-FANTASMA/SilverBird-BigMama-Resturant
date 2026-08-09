from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_auth_service
from app.domain.enums import RoleName
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.session import get_db_session
from app.schemas.auth import PrivilegedUserCreateRequest
from app.schemas.user import UserResponse

router = APIRouter(dependencies=[Depends(require_roles(RoleName.ADMIN))])


@router.post("", response_model=UserResponse)
def create_user(payload: PrivilegedUserCreateRequest, service: AuthService = Depends(get_auth_service)):
    return service.create_privileged_user(payload)


@router.get("", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_db_session)):
    return session.scalars(select(UserModel)).all()
