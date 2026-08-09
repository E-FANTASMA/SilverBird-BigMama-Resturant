from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.payment import PaymentModel
from app.infrastructure.database.repositories.base import SQLAlchemyRepository


class PaymentRepository(SQLAlchemyRepository[PaymentModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PaymentModel)

    def get_by_reference(self, reference: str) -> PaymentModel | None:
        return self.session.scalar(select(PaymentModel).where(PaymentModel.reference == reference))

    def list_by_order_id(self, order_id):
        statement = select(PaymentModel).where(PaymentModel.order_id == order_id).order_by(desc(PaymentModel.created_at))
        return self.session.scalars(statement).all()
