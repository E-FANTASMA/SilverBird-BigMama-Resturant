from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.database.models.cart import CartItemModel, CartModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class CartRepository(SQLAlchemyRepository[CartModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CartModel)

    def get_by_user_id(self, user_id):
        statement = (
            select(CartModel)
            .options(selectinload(CartModel.items).selectinload(CartItemModel.food_item))
            .where(CartModel.user_id == user_id)
        )
        return self.session.scalar(statement)
