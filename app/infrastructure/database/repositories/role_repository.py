from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import RoleName
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository[RoleModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RoleModel)

    def get_by_name(self, name: RoleName) -> RoleModel | None:
        return self.session.scalar(select(RoleModel).where(RoleModel.name == name.value))
