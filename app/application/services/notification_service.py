from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger, log_event
from app.domain.enums import NotificationChannel, NotificationDeliveryStatus, NotificationType
from app.infrastructure.database.models.notification import NotificationDeliveryModel, NotificationModel
from app.infrastructure.database.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreateRequest

logger = get_logger(__name__)


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
        log_event(logger, "notification_created", notification_id=notification.id, user_id=notification.user_id, type=notification.type)
        return notification

    def list_notifications(self, user_id):
        return self.notifications.list_by_user_id(user_id)

    def get_unread_count(self, user_id) -> int:
        return self.notifications.unread_count(user_id)

    def mark_as_read(self, user_id, notification_id):
        notification = self.notifications.get_by_user_id_and_id(user_id, notification_id)
        if not notification:
            raise NotFoundException("Notification not found")
        notification.is_read = True
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id) -> dict[str, str]:
        self.notifications.mark_all_read(user_id)
        self.session.commit()
        return {"message": "Notifications marked as read"}

    def create_order_notification(self, user_id, title: str, message: str) -> None:
        self._create_internal_notification(user_id, title, message, NotificationType.ORDER)

    def create_payment_notification(self, user_id, title: str, message: str) -> None:
        self._create_internal_notification(user_id, title, message, NotificationType.PAYMENT)

    def create_delivery_notification(self, user_id, title: str, message: str) -> None:
        self._create_internal_notification(user_id, title, message, NotificationType.DELIVERY)

    def _create_internal_notification(self, user_id, title: str, message: str, notification_type: NotificationType) -> None:
        self.session.add(NotificationModel(user_id=user_id, title=title, message=message, type=notification_type))
