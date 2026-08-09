from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import OrderStatus, OrderType, PaymentStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class OrderModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    order_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType, name="order_type_enum"), nullable=False)
    delivery_address_id: Mapped[str | None] = mapped_column(ForeignKey("delivery_addresses.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum"), default=OrderStatus.PENDING, nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    delivery_distance_km: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    table_number: Mapped[str | None] = mapped_column(String(30))
    scheduled_pickup_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"), default=PaymentStatus.PENDING, nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("UserModel", back_populates="orders")
    delivery_address = relationship("DeliveryAddressModel", lazy="selectin")
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("PaymentModel", back_populates="order", lazy="selectin")
    delivery = relationship("DeliveryModel", back_populates="order", uselist=False, lazy="selectin")


class OrderItemModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    food_item_id: Mapped[str] = mapped_column(ForeignKey("food_items.id"), nullable=False)
    food_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order = relationship("OrderModel", back_populates="items")
