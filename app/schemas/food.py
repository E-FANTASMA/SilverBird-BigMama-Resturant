from decimal import Decimal
from uuid import UUID

from app.schemas.common import SchemaBase, TimestampResponse


class FoodCreateRequest(SchemaBase):
    category_id: UUID
    name: str
    description: str | None = None
    price: Decimal
    preparation_time_minutes: int | None = None


class FoodUpdateRequest(SchemaBase):
    category_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    is_available: bool | None = None
    preparation_time_minutes: int | None = None


class FoodResponse(TimestampResponse):
    category_id: UUID
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    image_url: str | None = None
    image_path: str | None = None
    is_available: bool
    preparation_time_minutes: int | None = None
