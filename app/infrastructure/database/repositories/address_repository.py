from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.address import DeliveryAddressModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class AddressRepository(SQLAlchemyRepository[DeliveryAddressModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DeliveryAddressModel)

    def list_by_user_id(self, user_id):
        statement = (
            select(DeliveryAddressModel)
            .where(DeliveryAddressModel.user_id == user_id, DeliveryAddressModel.deleted_at.is_(None))
            .order_by(DeliveryAddressModel.is_default.desc(), DeliveryAddressModel.created_at.asc())
        )
        return self.session.scalars(statement).all()

    def get_by_user_id_and_id(self, user_id, address_id) -> DeliveryAddressModel | None:
        statement = select(DeliveryAddressModel).where(
            DeliveryAddressModel.user_id == user_id,
            DeliveryAddressModel.id == address_id,
            DeliveryAddressModel.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def get_default_by_user_id(self, user_id) -> DeliveryAddressModel | None:
        statement = select(DeliveryAddressModel).where(
            DeliveryAddressModel.user_id == user_id,
            DeliveryAddressModel.is_default.is_(True),
            DeliveryAddressModel.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def clear_default_for_user(self, user_id) -> None:
        for address in self.list_by_user_id(user_id):
            address.is_default = False
