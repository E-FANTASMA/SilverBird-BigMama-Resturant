from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class FoodRepository(SQLAlchemyRepository[FoodItemModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FoodItemModel)

    def list_active(self):
        return self.session.scalars(
            select(FoodItemModel)
            .where(FoodItemModel.deleted_at.is_(None))
            .order_by(FoodItemModel.name)
        ).all()

    def list_available(self):
        return self.session.scalars(
            select(FoodItemModel)
            .where(FoodItemModel.deleted_at.is_(None))
            .where(FoodItemModel.is_available.is_(True))
            .order_by(FoodItemModel.name)
        ).all()

    def get_active_by_slug(self, slug: str) -> FoodItemModel | None:
        return self.session.scalar(
            select(FoodItemModel).where(FoodItemModel.slug == slug).where(FoodItemModel.deleted_at.is_(None))
        )
