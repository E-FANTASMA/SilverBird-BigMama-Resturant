from app.schemas.common import SchemaBase, TimestampResponse


class CategoryCreateRequest(SchemaBase):
    name: str
    description: str | None = None
    sort_order: int = 0


class CategoryUpdateRequest(SchemaBase):
    name: str | None = None
    description: str | None = None
    sort_order: int | None = None


class CategoryResponse(TimestampResponse):
    name: str
    slug: str
    description: str | None = None
    sort_order: int
