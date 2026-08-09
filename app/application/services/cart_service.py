from decimal import Decimal

from sqlalchemy.orm import Session

from app.application.services.address_service import AddressService
from app.application.services.pricing_service import OrderPricingService
from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.database.models.cart import CartItemModel, CartModel
from app.infrastructure.database.repositories.cart_repository import CartRepository
from app.infrastructure.database.repositories.food_repository import FoodRepository
from app.schemas.cart import CartItemCreateRequest, CartItemResponse, CartItemUpdateRequest, CartResponse


class CartService:
    def __init__(self, session: Session, pricing_service: OrderPricingService) -> None:
        self.session = session
        self.carts = CartRepository(session)
        self.foods = FoodRepository(session)
        self.addresses = AddressService(session)
        self.pricing_service = pricing_service

    def get_cart(self, user_id):
        cart = self.carts.get_by_user_id(user_id)
        if not cart:
            cart = CartModel(user_id=user_id)
            self.carts.add(cart)
            self.session.commit()
            self.session.refresh(cart)
        return self._build_cart_response(user_id, cart)

    def add_item(self, user_id, payload: CartItemCreateRequest):
        cart = self._get_or_create_cart_model(user_id)
        food = self.foods.get(payload.food_item_id)
        if food.deleted_at is not None:
            raise ValidationException("Food item does not exist")
        if not food.is_available:
            raise ValidationException("Food item is unavailable")
        existing = next((item for item in cart.items if item.food_item_id == payload.food_item_id), None)
        if existing:
            existing.quantity += payload.quantity
            existing.subtotal = Decimal(existing.quantity) * existing.unit_price
        else:
            cart.items.append(
                CartItemModel(
                    food_item_id=food.id,
                    quantity=payload.quantity,
                    unit_price=food.price,
                    subtotal=Decimal(payload.quantity) * food.price,
                )
            )
        self.session.commit()
        self.session.refresh(cart)
        return self._build_cart_response(user_id, cart)

    def update_item(self, user_id, item_id, payload: CartItemUpdateRequest):
        cart = self._get_or_create_cart_model(user_id)
        item = next((entry for entry in cart.items if entry.id == item_id), None)
        if not item:
            raise NotFoundException("Cart item not found")
        if item.food_item.deleted_at is not None or not item.food_item.is_available:
            raise ValidationException("Food item is unavailable")
        item.quantity = payload.quantity
        item.subtotal = Decimal(payload.quantity) * item.unit_price
        self.session.commit()
        self.session.refresh(cart)
        return self._build_cart_response(user_id, cart)

    def remove_item(self, user_id, item_id):
        cart = self._get_or_create_cart_model(user_id)
        item = next((entry for entry in cart.items if entry.id == item_id), None)
        if not item:
            raise NotFoundException("Cart item not found")
        self.session.delete(item)
        self.session.commit()
        self.session.refresh(cart)
        return self._build_cart_response(user_id, cart)

    def clear_cart(self, user_id):
        cart = self._get_or_create_cart_model(user_id)
        for item in list(cart.items):
            self.session.delete(item)
        self.session.commit()
        self.session.refresh(cart)
        return self._build_cart_response(user_id, cart)

    def get_cart_model(self, user_id):
        return self._get_or_create_cart_model(user_id)

    def _get_or_create_cart_model(self, user_id):
        cart = self.carts.get_by_user_id(user_id)
        if not cart:
            cart = CartModel(user_id=user_id)
            self.carts.add(cart)
            self.session.commit()
            self.session.refresh(cart)
        return cart

    def _build_cart_response(self, user_id, cart: CartModel) -> CartResponse:
        subtotal = sum((item.subtotal for item in cart.items), start=Decimal("0.00"))
        delivery_fee = Decimal("0.00")
        default_address = self.addresses.get_default_address(user_id)
        if cart.items and default_address and default_address.latitude is not None and default_address.longitude is not None:
            distance = self.pricing_service.calculate_delivery_distance_km(
                float(default_address.latitude),
                float(default_address.longitude),
            )
            delivery_fee = self.pricing_service.calculate_delivery_fee(distance)
        tax_amount = Decimal("0.00")
        discount_amount = Decimal("0.00")
        grand_total = subtotal + delivery_fee + tax_amount - discount_amount
        total_items = sum(item.quantity for item in cart.items)

        items = [
            CartItemResponse(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                cart_id=item.cart_id,
                food_item_id=item.food_item_id,
                food_name=item.food_item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in cart.items
        ]
        return CartResponse(
            id=cart.id,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
            user_id=cart.user_id,
            items=items,
            total_items=total_items,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            grand_total=grand_total,
        )
