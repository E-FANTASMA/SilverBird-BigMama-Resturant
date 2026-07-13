from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampResponse


class CartItemCreateRequest(BaseModel):
    food_item_id: UUID
    quantity: int = Field(gt=0)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(TimestampResponse):
    cart_id: UUID
    food_item_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class CartResponse(TimestampResponse):
    user_id: UUID
    items: list[CartItemResponse]
