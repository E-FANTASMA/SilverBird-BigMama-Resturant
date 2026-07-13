from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampResponse


class AddressCreateRequest(BaseModel):
    label: str
    address: str
    city: str
    state: str
    phone: str
    latitude: float
    longitude: float
    is_default: bool = False


class AddressUpdateRequest(BaseModel):
    label: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool | None = None


class AddressResponse(TimestampResponse):
    user_id: UUID
    label: str
    address: str
    city: str
    state: str
    phone: str
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool
