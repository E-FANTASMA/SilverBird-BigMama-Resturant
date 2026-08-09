from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.application.services.notification_service import NotificationService
from app.core.exceptions import ForbiddenException, ValidationException
from app.core.logging import get_logger, log_event
from app.domain.enums import DeliveryStatus, OrderStatus
from app.infrastructure.database.models.delivery import DeliveryModel
from app.infrastructure.database.repositories.address_repository import AddressRepository
from app.infrastructure.database.repositories.delivery_repository import DeliveryRepository
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.schemas.delivery import DeliveryAssignRequest, DeliveryStatusUpdateRequest


class DeliveryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.deliveries = DeliveryRepository(session)
        self.orders = OrderRepository(session)
        self.addresses = AddressRepository(session)
        self.users = UserRepository(session)
        self.notifications = NotificationService(session)

    def assign_delivery(self, order_id, payload: DeliveryAssignRequest):
        order = self.orders.get(order_id)
        if order.order_type.value != "DELIVERY":
            raise ValidationException("Only delivery orders can be assigned to delivery personnel")
        if order.payment_status.value != "SUCCESSFUL":
            raise ValidationException("Only paid delivery orders can be assigned")

        delivery_personnel = self.users.get(payload.delivery_personnel_id)
        if not delivery_personnel.role or delivery_personnel.role.name != "DELIVERY_PERSONNEL":
            raise ValidationException("Assigned user must be delivery personnel")

        address_id = payload.delivery_address_id or order.delivery_address_id
        if not address_id:
            raise ValidationException("Delivery address is required")
        address = self.addresses.get(address_id)

        delivery = self.deliveries.get_by_order_id(order.id)
        if delivery:
            delivery.delivery_personnel_id = payload.delivery_personnel_id
            delivery.delivery_address_id = address.id
            delivery.estimated_delivery_time = payload.estimated_delivery_time
            delivery.status = DeliveryStatus.ASSIGNED
        else:
            delivery = DeliveryModel(
                order_id=order.id,
                delivery_personnel_id=payload.delivery_personnel_id,
                delivery_address_id=address.id,
                status=DeliveryStatus.ASSIGNED,
                estimated_delivery_time=payload.estimated_delivery_time,
            )
            self.session.add(delivery)
        order.status = OrderStatus.OUT_FOR_DELIVERY
        self.session.commit()
        self.notifications.create_delivery_notification(
            order.user_id,
            "Out For Delivery",
            f"Order {order.order_number} has been assigned to a delivery rider.",
        )
        self.session.commit()
        log_event(logger, "delivery_assigned", order_id=order.id, delivery_personnel_id=payload.delivery_personnel_id)
        return self.deliveries.get_by_order_id(order.id)

    def list_assigned_deliveries(self, user_id):
        return self.deliveries.list_by_personnel_id(user_id)

    def update_delivery_status(self, user_id, delivery_id, payload: DeliveryStatusUpdateRequest):
        delivery = self.deliveries.get_for_display(delivery_id) or self.deliveries.get(delivery_id)
        if str(delivery.delivery_personnel_id) != str(user_id):
            raise ForbiddenException("You can only update your assigned deliveries")
        allowed_transitions = {
            DeliveryStatus.ASSIGNED: {DeliveryStatus.PICKED_UP, DeliveryStatus.FAILED},
            DeliveryStatus.PICKED_UP: {DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELIVERED, DeliveryStatus.FAILED},
            DeliveryStatus.IN_TRANSIT: {DeliveryStatus.DELIVERED, DeliveryStatus.FAILED},
            DeliveryStatus.DELIVERED: set(),
            DeliveryStatus.FAILED: set(),
        }
        if payload.status not in allowed_transitions[delivery.status]:
            raise ValidationException(f"Cannot change delivery status from {delivery.status} to {payload.status}")
        delivery.status = payload.status
        if payload.status == DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = datetime.now(UTC)
            delivery.order.status = OrderStatus.OUT_FOR_DELIVERY
            self.notifications.create_delivery_notification(
                delivery.order.user_id,
                "Order Picked Up",
                f"Order {delivery.order.order_number} has been picked up by the delivery rider.",
            )
        if payload.status == DeliveryStatus.IN_TRANSIT:
            delivery.order.status = OrderStatus.OUT_FOR_DELIVERY
            self.notifications.create_delivery_notification(
                delivery.order.user_id,
                "Out For Delivery",
                f"Order {delivery.order.order_number} is on the way.",
            )
        if payload.status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = datetime.now(UTC)
            delivery.order.status = OrderStatus.DELIVERED
            self.notifications.create_delivery_notification(
                delivery.order.user_id,
                "Delivered",
                f"Order {delivery.order.order_number} has been delivered successfully.",
            )
        if payload.status == DeliveryStatus.FAILED:
            delivery.order.status = OrderStatus.READY
            self.notifications.create_delivery_notification(
                delivery.order.user_id,
                "Delivery Update",
                f"Delivery attempt for order {delivery.order.order_number} could not be completed.",
            )
        self.session.commit()
        log_event(logger, "delivery_status_updated", delivery_id=delivery.id, order_id=delivery.order_id, status=delivery.status)
        return self.deliveries.get_for_display(delivery.id)

    def get_customer_contact(self, user_id, delivery_id):
        delivery = self.deliveries.get_for_display(delivery_id) or self.deliveries.get(delivery_id)
        if str(delivery.delivery_personnel_id) != str(user_id):
            raise ForbiddenException("You can only access your assigned deliveries")
        return {
            "order_id": delivery.order_id,
            "customer_name": f"{delivery.order.user.first_name} {delivery.order.user.last_name}",
            "customer_phone": delivery.order.user.phone,
            "delivery_address": delivery.address.address if delivery.address else None,
            "city": delivery.address.city if delivery.address else None,
            "state": delivery.address.state if delivery.address else None,
        }


logger = get_logger(__name__)
