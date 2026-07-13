from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import PaymentStatus


class PaymentInitializeResponse(BaseModel):
    order_id: UUID
    reference: str
    authorization_url: str
    amount: Decimal
    status: PaymentStatus


class PaymentVerifyResponse(BaseModel):
    reference: str
    status: PaymentStatus
    paid_at: datetime | None = None
