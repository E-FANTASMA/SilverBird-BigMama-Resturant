from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[UserModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UserModel)

    def get_by_email(self, email: str) -> UserModel | None:
        statement = select(UserModel).where(func.lower(UserModel.email) == email.lower())
        return self.session.scalar(statement)
