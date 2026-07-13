from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.database.models.order import OrderModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[OrderModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OrderModel)

    def list_by_user_id(self, user_id):
        statement = (
            select(OrderModel)
            .options(selectinload(OrderModel.items), selectinload(OrderModel.payments), selectinload(OrderModel.delivery))
            .where(OrderModel.user_id == user_id)
        )
        return self.session.scalars(statement).all()
