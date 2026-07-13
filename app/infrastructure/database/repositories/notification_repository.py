from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.notification import NotificationModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository[NotificationModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, NotificationModel)

    def list_by_user_id(self, user_id):
        return self.session.scalars(select(NotificationModel).where(NotificationModel.user_id == user_id)).all()
