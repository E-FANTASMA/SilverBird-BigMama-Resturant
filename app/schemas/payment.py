from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import PaymentStatus


class PaymentInitializeRequest(BaseModel):
    order_id: UUID


class PaymentInitializeResponse(BaseModel):
    order_id: UUID
    reference: str
    authorization_url: str
    amount: Decimal
    status: PaymentStatus


class PaymentVerifyResponse(BaseModel):
    order_id: UUID
    reference: str
    status: PaymentStatus
    gateway_response: str | None = None
    paid_at: datetime | None = None


class PaystackWebhookRequest(BaseModel):
    event: str = Field(min_length=1)
    data: dict
