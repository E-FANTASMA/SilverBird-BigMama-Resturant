from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CartModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "carts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)

    user = relationship("UserModel", back_populates="cart")
    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan", lazy="selectin")


class CartItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "food_item_id", name="uq_cart_food"),)

    cart_id: Mapped[str] = mapped_column(ForeignKey("carts.id"), nullable=False, index=True)
    food_item_id: Mapped[str] = mapped_column(ForeignKey("food_items.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    cart = relationship("CartModel", back_populates="items")
    food_item = relationship("FoodItemModel", lazy="selectin")
