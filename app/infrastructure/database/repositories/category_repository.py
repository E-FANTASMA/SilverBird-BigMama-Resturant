from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.category import CategoryModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository[CategoryModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CategoryModel)

    def list_active(self):
        return self.session.scalars(
            select(CategoryModel).where(CategoryModel.deleted_at.is_(None)).order_by(CategoryModel.sort_order, CategoryModel.name)
        ).all()

    def get_by_slug(self, slug: str) -> CategoryModel | None:
        return self.session.scalar(
            select(CategoryModel).where(CategoryModel.slug == slug).where(CategoryModel.deleted_at.is_(None))
        )
