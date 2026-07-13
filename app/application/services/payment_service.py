from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.domain.enums import OrderStatus, PaymentStatus
from app.infrastructure.database.models.payment import PaymentModel
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentInitializeResponse, PaymentVerifyResponse


class PaymentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.payments = PaymentRepository(session)

    def initialize_payment(self, order_id, user_id=None, is_admin: bool = False) -> PaymentInitializeResponse:
        order = self.orders.get(order_id)
        if not is_admin and user_id is not None and str(order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this order")
        reference = f"paystack_{uuid4().hex}"
        payment = PaymentModel(
            order_id=order.id,
            reference=reference,
            amount=Decimal(order.total),
            status=PaymentStatus.PENDING,
        )
        self.session.add(payment)
        self.session.commit()
        return PaymentInitializeResponse(
            order_id=order.id,
            reference=reference,
            authorization_url=f"https://checkout.paystack.com/{reference}",
            amount=order.total,
            status=payment.status,
        )

    def verify_payment(self, reference: str, user_id=None, is_admin: bool = False) -> PaymentVerifyResponse:
        payment = self.payments.get_by_reference(reference)
        if not payment:
            raise NotFoundException("Payment reference not found")
        if not is_admin and user_id is not None and str(payment.order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this payment")
        payment.status = PaymentStatus.SUCCESSFUL
        payment.paid_at = datetime.now(UTC)
        payment.order.payment_status = PaymentStatus.SUCCESSFUL
        if payment.order.status == OrderStatus.PENDING:
            payment.order.status = OrderStatus.CONFIRMED
        self.session.commit()
        return PaymentVerifyResponse(reference=payment.reference, status=payment.status, paid_at=payment.paid_at)
