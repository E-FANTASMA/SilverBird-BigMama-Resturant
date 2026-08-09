from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.database.models.delivery import DeliveryModel
from app.infrastructure.database.models.order import OrderModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class DeliveryRepository(SQLAlchemyRepository[DeliveryModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DeliveryModel)

    def list_by_personnel_id(self, user_id):
        statement = (
            select(DeliveryModel)
            .options(selectinload(DeliveryModel.order), selectinload(DeliveryModel.address))
            .where(DeliveryModel.delivery_personnel_id == user_id)
            .order_by(DeliveryModel.created_at.desc())
        )
        return self.session.scalars(statement).all()

    def get_for_display(self, delivery_id):
        statement = (
            select(DeliveryModel)
            .options(selectinload(DeliveryModel.order).selectinload(OrderModel.user), selectinload(DeliveryModel.address))
            .where(DeliveryModel.id == delivery_id)
        )
        return self.session.scalar(statement)

    def get_by_order_id(self, order_id):
        statement = (
            select(DeliveryModel)
            .options(selectinload(DeliveryModel.order).selectinload(OrderModel.user), selectinload(DeliveryModel.address))
            .where(DeliveryModel.order_id == order_id)
        )
        return self.session.scalar(statement)
