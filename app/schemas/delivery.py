from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import DeliveryStatus
from app.schemas.common import TimestampResponse


class DeliveryAssignRequest(BaseModel):
    delivery_personnel_id: UUID
    delivery_address_id: UUID | None = None
    estimated_delivery_time: datetime | None = None


class DeliveryStatusUpdateRequest(BaseModel):
    status: DeliveryStatus


class DeliveryContactResponse(BaseModel):
    order_id: UUID
    customer_name: str
    customer_phone: str | None = None
    delivery_address: str | None = None
    city: str | None = None
    state: str | None = None


class DeliveryResponse(TimestampResponse):
    order_id: UUID
    delivery_personnel_id: UUID
    delivery_address_id: UUID
    status: DeliveryStatus
    estimated_delivery_time: datetime | None = None
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None
