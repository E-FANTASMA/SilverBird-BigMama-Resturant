from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.application.services.pricing_service import OrderPricingService
from app.core.exceptions import ForbiddenException, ValidationException
from app.domain.enums import OrderStatus, OrderType, PaymentStatus
from app.infrastructure.database.models.order import OrderItemModel, OrderModel
from app.infrastructure.database.repositories.address_repository import AddressRepository
from app.infrastructure.database.repositories.cart_repository import CartRepository
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreateRequest


class OrderService:
    def __init__(self, session: Session, pricing_service: OrderPricingService) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.carts = CartRepository(session)
        self.addresses = AddressRepository(session)
        self.pricing_service = pricing_service

    def create_order(self, user_id, payload: OrderCreateRequest):
        cart = self.carts.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValidationException("Cart is empty")

        subtotal = sum((item.subtotal for item in cart.items), start=Decimal("0.00"))
        delivery_fee = Decimal("0.00")
        distance_km = None

        if payload.order_type == OrderType.DELIVERY:
            if not payload.delivery_address_id:
                raise ValidationException("Delivery address is required")
            address = self.addresses.get(payload.delivery_address_id)
            if address.latitude is None or address.longitude is None:
                raise ValidationException("Delivery address coordinates are required")
            distance_km = self.pricing_service.calculate_delivery_distance_km(float(address.latitude), float(address.longitude))
            delivery_fee = self.pricing_service.calculate_delivery_fee(distance_km)
        elif payload.order_type == OrderType.PICKUP and not payload.scheduled_pickup_time:
            raise ValidationException("Scheduled pickup time is required for pickup orders")

        order = OrderModel(
            user_id=user_id,
            order_number=f"PX-{datetime.now(UTC):%Y%m%d}-{str(uuid4())[:8].upper()}",
            order_type=payload.order_type,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            delivery_distance_km=distance_km,
            total=subtotal + delivery_fee,
            notes=payload.notes,
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
        return order

    def list_orders(self, user_id):
        return self.orders.list_by_user_id(user_id)

    def get_order(self, order_id, user_id=None, is_admin: bool = False):
        order = self.orders.get(order_id)
        if not is_admin and user_id is not None and str(order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this order")
        return order
