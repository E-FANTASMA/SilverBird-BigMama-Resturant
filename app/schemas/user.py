from uuid import UUID

from pydantic import EmailStr

from app.schemas.common import ORMBaseSchema, TimestampResponse


class UserResponse(TimestampResponse):
    role_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    is_verified: bool
    is_active: bool


class ProfileUpdateRequest(ORMBaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
