from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.database.models.notification import NotificationModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository[NotificationModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, NotificationModel)

    def list_by_user_id(self, user_id):
        statement = (
            select(NotificationModel)
            .options(selectinload(NotificationModel.deliveries))
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
        )
        return self.session.scalars(statement).all()

    def get_by_user_id_and_id(self, user_id, notification_id):
        statement = (
            select(NotificationModel)
            .options(selectinload(NotificationModel.deliveries))
            .where(NotificationModel.user_id == user_id, NotificationModel.id == notification_id)
        )
        return self.session.scalar(statement)

    def unread_count(self, user_id) -> int:
        return self.session.scalar(
            select(func.count()).select_from(NotificationModel).where(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read.is_(False),
            )
        ) or 0

    def mark_all_read(self, user_id) -> None:
        self.session.execute(update(NotificationModel).where(NotificationModel.user_id == user_id).values(is_read=True))
