from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.address import DeliveryAddressModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class AddressRepository(SQLAlchemyRepository[DeliveryAddressModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DeliveryAddressModel)

    def list_by_user_id(self, user_id):
        return self.session.scalars(select(DeliveryAddressModel).where(DeliveryAddressModel.user_id == user_id)).all()
