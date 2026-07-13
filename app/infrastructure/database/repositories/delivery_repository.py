from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.delivery import DeliveryModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class DeliveryRepository(SQLAlchemyRepository[DeliveryModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DeliveryModel)

    def list_by_personnel_id(self, user_id):
        return self.session.scalars(select(DeliveryModel).where(DeliveryModel.delivery_personnel_id == user_id)).all()
