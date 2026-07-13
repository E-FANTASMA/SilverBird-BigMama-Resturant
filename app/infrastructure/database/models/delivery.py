from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import DeliveryStatus
from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "deliveries"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False, unique=True)
    delivery_personnel_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    delivery_address_id: Mapped[str] = mapped_column(ForeignKey("delivery_addresses.id"), nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status_enum"), default=DeliveryStatus.ASSIGNED, nullable=False
    )
    estimated_delivery_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order = relationship("OrderModel", back_populates="delivery")
    address = relationship("DeliveryAddressModel", lazy="selectin")
