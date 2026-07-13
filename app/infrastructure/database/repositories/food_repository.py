from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class FoodRepository(SQLAlchemyRepository[FoodItemModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FoodItemModel)

    def list_available(self):
        return self.session.scalars(select(FoodItemModel).where(FoodItemModel.is_available.is_(True))).all()
