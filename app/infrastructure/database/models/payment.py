from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import PaymentStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="PAYSTACK")
    payment_method: Mapped[str | None] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"), default=PaymentStatus.PENDING, nullable=False
    )
    gateway_response: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(10), default="NGN", nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order = relationship("OrderModel", back_populates="payments")


class PaymentWebhookEventModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_webhook_events"

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    signature: Mapped[str | None] = mapped_column(Text)
    processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
