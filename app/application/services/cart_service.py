from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.database.models.cart import CartItemModel, CartModel
from app.infrastructure.database.repositories.cart_repository import CartRepository
from app.infrastructure.database.repositories.food_repository import FoodRepository
from app.schemas.cart import CartItemCreateRequest, CartItemUpdateRequest


class CartService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.carts = CartRepository(session)
        self.foods = FoodRepository(session)

    def get_cart(self, user_id):
        cart = self.carts.get_by_user_id(user_id)
        if not cart:
            cart = CartModel(user_id=user_id)
            self.carts.add(cart)
            self.session.commit()
            self.session.refresh(cart)
        return cart

    def add_item(self, user_id, payload: CartItemCreateRequest):
        cart = self.get_cart(user_id)
        food = self.foods.get(payload.food_item_id)
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
        return cart

    def update_item(self, user_id, item_id, payload: CartItemUpdateRequest):
        cart = self.get_cart(user_id)
        item = next((entry for entry in cart.items if entry.id == item_id), None)
        if not item:
            raise NotFoundException("Cart item not found")
        item.quantity = payload.quantity
        item.subtotal = Decimal(payload.quantity) * item.unit_price
        self.session.commit()
        self.session.refresh(cart)
        return cart

    def remove_item(self, user_id, item_id):
        cart = self.get_cart(user_id)
        item = next((entry for entry in cart.items if entry.id == item_id), None)
        if not item:
            raise NotFoundException("Cart item not found")
        self.session.delete(item)
        self.session.commit()
        self.session.refresh(cart)
        return cart
