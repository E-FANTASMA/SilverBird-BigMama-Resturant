from uuid import UUID

import re

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.constants import NIGERIAN_STATES
from app.schemas.common import TimestampResponse

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


class AddressValidationMixin(BaseModel):
    @field_validator("phone", mode="before", check_fields=False)
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = re.sub(r"[\s\-()]", "", value)
        if not PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("Phone number must be in a valid international format")
        return normalized

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def normalize_state(cls, value: str) -> str:
        normalized = " ".join(part for part in value.strip().upper().split())
        if normalized not in NIGERIAN_STATES:
            raise ValueError("State must be a valid Nigerian state or FCT")
        return normalized.title() if normalized != "FCT" else "FCT"

    @model_validator(mode="after")
    def validate_coordinates(self):
        latitude = getattr(self, "latitude", None)
        longitude = getattr(self, "longitude", None)
        if (latitude is None) != (longitude is None):
            raise ValueError("Latitude and longitude must be provided together")
        return self


class AddressCreateRequest(AddressValidationMixin):
    label: str = Field(min_length=1, max_length=80)
    address: str = Field(min_length=5, max_length=500)
    city: str = Field(min_length=1, max_length=100)
    state: str
    phone: str
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool = False


class AddressUpdateRequest(AddressValidationMixin):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    address: str | None = Field(default=None, min_length=5, max_length=500)
    city: str | None = Field(default=None, min_length=1, max_length=100)
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
