from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import OrderStatus, OrderType, PaymentStatus
from app.schemas.common import ORMBaseSchema, TimestampResponse


class OrderCreateRequest(BaseModel):
    order_type: OrderType
    delivery_address_id: UUID | None = None
    notes: str | None = None
    scheduled_pickup_time: datetime | None = None
    table_number: str | None = None


class OrderItemResponse(ORMBaseSchema):
    id: UUID
    food_item_id: UUID
    food_name_snapshot: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(TimestampResponse):
    user_id: UUID
    order_number: str
    order_type: OrderType
    delivery_address_id: UUID | None = None
    status: OrderStatus
    subtotal: Decimal
    delivery_fee: Decimal
    delivery_distance_km: Decimal | None = None
    total: Decimal
    notes: str | None = None
    table_number: str | None = None
    scheduled_pickup_time: datetime | None = None
    payment_status: PaymentStatus
    items: list[OrderItemResponse]
