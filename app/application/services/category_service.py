from slugify import slugify
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException
from app.infrastructure.database.models.category import CategoryModel
from app.infrastructure.database.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.categories = CategoryRepository(session)

    def list_categories(self):
        return self.categories.list()

    def create_category(self, payload: CategoryCreateRequest):
        slug = slugify(payload.name)
        if self.categories.get_by_slug(slug):
            raise ConflictException("Category already exists")
        category = CategoryModel(name=payload.name, slug=slug, description=payload.description, sort_order=payload.sort_order)
        self.categories.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def update_category(self, category_id, payload: CategoryUpdateRequest):
        category = self.categories.get(category_id)
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            updates["slug"] = slugify(updates["name"])
        for field, value in updates.items():
            setattr(category, field, value)
        self.session.commit()
        self.session.refresh(category)
        return category
