import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.enums import NotificationChannel, NotificationDeliveryStatus, NotificationType
from app.schemas.common import TimestampResponse

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


class NotificationCreateRequest(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=1000)
    type: NotificationType
    email_recipient: EmailStr | None = None
    sms_recipient: str | None = None

    @field_validator("sms_recipient")
    @classmethod
    def validate_sms_recipient(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = re.sub(r"[\s\-()]", "", value)
        if not PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("SMS recipient phone number must be in a valid international format")
        return normalized


class NotificationDeliveryResponse(TimestampResponse):
    notification_id: UUID
    channel: NotificationChannel
    recipient: str
    status: NotificationDeliveryStatus
    provider: str | None = None
    provider_message_id: str | None = None
    error_message: str | None = None


class NotificationResponse(TimestampResponse):
    user_id: UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
    deliveries: list[NotificationDeliveryResponse] = []


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
