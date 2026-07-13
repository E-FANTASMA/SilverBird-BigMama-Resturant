from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.enums import NotificationType
from app.schemas.common import TimestampResponse


class NotificationCreateRequest(BaseModel):
    user_id: UUID
    title: str
    message: str
    type: NotificationType
    email_recipient: EmailStr | None = None
    sms_recipient: str | None = None


class NotificationResponse(TimestampResponse):
    user_id: UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
