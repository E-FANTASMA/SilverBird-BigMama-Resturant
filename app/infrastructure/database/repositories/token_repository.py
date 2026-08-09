from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.token import PasswordResetTokenModel, RefreshTokenModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository[RefreshTokenModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RefreshTokenModel)

    def list_active_by_user_id(self, user_id):
        statement = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.revoked_at.is_(None))
        )
        return self.session.scalars(statement).all()

    def revoke(self, token: RefreshTokenModel) -> None:
        token.revoked_at = datetime.now(UTC)

    def revoke_all_for_user(self, user_id) -> None:
        for token in self.list_active_by_user_id(user_id):
            self.revoke(token)


class PasswordResetTokenRepository(SQLAlchemyRepository[PasswordResetTokenModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PasswordResetTokenModel)

    def list_active(self):
        statement = select(PasswordResetTokenModel).where(PasswordResetTokenModel.used_at.is_(None))
        return self.session.scalars(statement).all()

    def list_active_by_user_id(self, user_id):
        statement = (
            select(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.user_id == user_id)
            .where(PasswordResetTokenModel.used_at.is_(None))
        )
        return self.session.scalars(statement).all()
