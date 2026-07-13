from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.domain.enums import DeliveryStatus, OrderStatus
from app.infrastructure.database.models.delivery import DeliveryModel
from app.infrastructure.database.repositories.delivery_repository import DeliveryRepository
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.schemas.delivery import DeliveryAssignRequest, DeliveryStatusUpdateRequest


class DeliveryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.deliveries = DeliveryRepository(session)
        self.orders = OrderRepository(session)

    def assign_delivery(self, order_id, payload: DeliveryAssignRequest):
        order = self.orders.get(order_id)
        delivery = DeliveryModel(
            order_id=order.id,
            delivery_personnel_id=payload.delivery_personnel_id,
            delivery_address_id=payload.delivery_address_id,
            status=DeliveryStatus.ASSIGNED,
            estimated_delivery_time=payload.estimated_delivery_time,
        )
        self.session.add(delivery)
        order.status = OrderStatus.OUT_FOR_DELIVERY
        self.session.commit()
        self.session.refresh(delivery)
        return delivery

    def list_assigned_deliveries(self, user_id):
        return self.deliveries.list_by_personnel_id(user_id)

    def update_delivery_status(self, user_id, delivery_id, payload: DeliveryStatusUpdateRequest):
        delivery = self.deliveries.get(delivery_id)
        if str(delivery.delivery_personnel_id) != str(user_id):
            raise ForbiddenException("You can only update your assigned deliveries")
        delivery.status = payload.status
        if payload.status == DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = datetime.now(UTC)
        if payload.status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = datetime.now(UTC)
            delivery.order.status = OrderStatus.DELIVERED
        self.session.commit()
        self.session.refresh(delivery)
        return delivery
