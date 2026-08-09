from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.application.services.address_service import AddressService
from app.application.services.cart_service import CartService
from app.application.services.notification_service import NotificationService
from app.application.services.pricing_service import OrderPricingService
from app.core.logging import get_logger, log_event
from app.core.exceptions import ForbiddenException, ValidationException
from app.domain.enums import OrderStatus, OrderType, PaymentStatus
from app.infrastructure.database.models.order import OrderItemModel, OrderModel
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreateRequest


class OrderService:
    def __init__(
        self,
        session: Session,
        pricing_service: OrderPricingService,
        address_service: AddressService,
        cart_service: CartService,
    ) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.pricing_service = pricing_service
        self.addresses = address_service
        self.carts = cart_service
        self.notifications = NotificationService(session)

    def create_order(self, user_id, payload: OrderCreateRequest):
        cart = self.carts.get_cart_model(user_id)
        if not cart or not cart.items:
            raise ValidationException("Cart is empty")

        subtotal = sum((item.subtotal for item in cart.items), start=Decimal("0.00"))
        delivery_fee = Decimal("0.00")
        distance_km = None
        delivery_address_id = None

        for item in cart.items:
            if item.food_item.deleted_at is not None or not item.food_item.is_available:
                raise ValidationException(f"{item.food_item.name} is no longer available")

        if payload.order_type == OrderType.DELIVERY:
            if not payload.delivery_address_id:
                raise ValidationException("Delivery address is required")
            address = self.addresses.validate_delivery_address(user_id, payload.delivery_address_id)
            distance_km = self.pricing_service.calculate_delivery_distance_km(float(address.latitude), float(address.longitude))
            delivery_fee = self.pricing_service.calculate_delivery_fee(distance_km)
            delivery_address_id = address.id
        elif payload.order_type == OrderType.PICKUP:
            if not payload.scheduled_pickup_time:
                raise ValidationException("Scheduled pickup time is required for pickup orders")
            if payload.scheduled_pickup_time <= datetime.now(UTC):
                raise ValidationException("Scheduled pickup time must be in the future")
        elif payload.delivery_address_id:
            raise ValidationException("Delivery address can only be used for delivery orders")

        if payload.order_type == OrderType.DINE_IN and payload.scheduled_pickup_time is not None:
            raise ValidationException("Pickup time is only supported for pickup orders")
        if payload.order_type != OrderType.DINE_IN and payload.table_number:
            raise ValidationException("Table number is only supported for dine-in orders")

        order = OrderModel(
            user_id=user_id,
            order_number=f"SBBM-{datetime.now(UTC):%Y%m%d}-{str(uuid4())[:8].upper()}",
            order_type=payload.order_type,
            delivery_address_id=delivery_address_id,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            delivery_distance_km=distance_km,
            total=subtotal + delivery_fee,
            notes=payload.notes,
            table_number=payload.table_number,
            scheduled_pickup_time=payload.scheduled_pickup_time,
            payment_status=PaymentStatus.PENDING,
        )
        self.session.add(order)
        self.session.flush()

        for item in cart.items:
            self.session.add(
                OrderItemModel(
                    order_id=order.id,
                    food_item_id=item.food_item_id,
                    food_name_snapshot=item.food_item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                    created_at=datetime.now(UTC),
                )
            )

        for item in list(cart.items):
            self.session.delete(item)

        self.session.commit()
        self.session.refresh(order)
        self.notifications.create_order_notification(
            user_id,
            "Order Created",
            f"Order {order.order_number} has been created successfully.",
        )
        self.session.commit()
        log_event(logger, "order_created", user_id=user_id, order_id=order.id, order_number=order.order_number)
        return self.orders.get_for_display(order.id)

    def list_orders(self, user_id):
        return self.orders.list_by_user_id(user_id)

    def get_order(self, order_id, user_id=None, is_admin: bool = False):
        order = self.orders.get_for_display(order_id) or self.orders.get(order_id)
        if not is_admin and user_id is not None and str(order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this order")
        return order


logger = get_logger(__name__)
