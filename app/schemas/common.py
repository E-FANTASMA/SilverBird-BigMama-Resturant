from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    pass


class ORMBaseSchema(SchemaBase):
    model_config = ConfigDict(from_attributes=True)


class TimestampResponse(ORMBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
