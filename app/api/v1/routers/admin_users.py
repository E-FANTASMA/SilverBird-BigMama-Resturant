from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import require_roles
from app.domain.enums import RoleName
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.session import get_db_session
from app.schemas.user import UserResponse

router = APIRouter(dependencies=[Depends(require_roles(RoleName.ADMIN))])


@router.get("", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_db_session)):
    return session.scalars(select(UserModel)).all()
