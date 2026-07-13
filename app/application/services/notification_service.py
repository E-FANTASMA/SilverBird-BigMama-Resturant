from sqlalchemy.orm import Session

from app.domain.enums import NotificationChannel, NotificationDeliveryStatus, NotificationType
from app.infrastructure.database.models.notification import NotificationDeliveryModel, NotificationModel
from app.infrastructure.database.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreateRequest


class NotificationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.notifications = NotificationRepository(session)

    def create_notification(self, payload: NotificationCreateRequest):
        notification = NotificationModel(
            user_id=payload.user_id,
            title=payload.title,
            message=payload.message,
            type=payload.type,
        )
        self.session.add(notification)
        self.session.flush()

        if payload.email_recipient:
            self.session.add(
                NotificationDeliveryModel(
                    notification_id=notification.id,
                    channel=NotificationChannel.EMAIL,
                    recipient=payload.email_recipient,
                    status=NotificationDeliveryStatus.PENDING,
                    provider="SMTP",
                )
            )
        if payload.sms_recipient:
            self.session.add(
                NotificationDeliveryModel(
                    notification_id=notification.id,
                    channel=NotificationChannel.SMS,
                    recipient=payload.sms_recipient,
                    status=NotificationDeliveryStatus.PENDING,
                    provider="SMS_PROVIDER",
                )
            )

        self.session.commit()
        self.session.refresh(notification)
        return notification

    def list_notifications(self, user_id):
        return self.notifications.list_by_user_id(user_id)
