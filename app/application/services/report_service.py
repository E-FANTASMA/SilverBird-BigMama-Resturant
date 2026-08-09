from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.orm import Session

from app.domain.enums import OrderStatus, PaymentStatus, RoleName
from app.infrastructure.database.models.category import CategoryModel
from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.models.order import OrderItemModel, OrderModel
from app.infrastructure.database.models.payment import PaymentModel
from app.infrastructure.database.models.user import UserModel


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def dashboard_summary(self) -> dict:
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        return {
            "total_users": self._count(select(func.count()).select_from(UserModel)),
            "total_customers": self._count_by_role(RoleName.CUSTOMER),
            "total_admins": self._count_by_role(RoleName.ADMIN),
            "total_delivery_personnel": self._count_by_role(RoleName.DELIVERY_PERSONNEL),
            "total_categories": self._count(select(func.count()).select_from(CategoryModel)),
            "total_foods": self._count(select(func.count()).select_from(FoodItemModel)),
            "available_foods": self._count(
                select(func.count()).select_from(FoodItemModel).where(FoodItemModel.is_available.is_(True))
            ),
            "unavailable_foods": self._count(
                select(func.count()).select_from(FoodItemModel).where(FoodItemModel.is_available.is_(False))
            ),
            "total_orders": self._count(select(func.count()).select_from(OrderModel)),
            "pending_orders": self._count_orders_by_status(OrderStatus.PENDING),
            "preparing_orders": self._count_orders_by_status(OrderStatus.PREPARING),
            "ready_orders": self._count_orders_by_status(OrderStatus.READY),
            "out_for_delivery_orders": self._count_orders_by_status(OrderStatus.OUT_FOR_DELIVERY),
            "delivered_orders": self._count_orders_by_status(OrderStatus.DELIVERED),
            "cancelled_orders": self._count_orders_by_status(OrderStatus.CANCELLED),
            "today_revenue": self._revenue_between(today_start, today_start + timedelta(days=1)),
            "weekly_revenue": self._revenue_between(datetime.now(UTC) - timedelta(days=7), datetime.now(UTC) + timedelta(seconds=1)),
            "monthly_revenue": self._revenue_between(datetime.now(UTC) - timedelta(days=30), datetime.now(UTC) + timedelta(seconds=1)),
            "average_order_value": self._average_order_value(),
            "top_selling_foods": self.top_selling_foods(limit=5),
            "top_customers": self.top_customers(limit=5),
            "recent_orders": self.recent_orders(limit=5),
        }

    def revenue_report(self, period: str | None = None, start_date: date | None = None, end_date: date | None = None) -> dict:
        start, end = self._resolve_period(period, start_date, end_date)
        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "revenue": self._revenue_between(start, end),
            "successful_payments": self._successful_payments_between(start, end),
        }

    def orders_report(self, period: str | None = None, start_date: date | None = None, end_date: date | None = None) -> dict:
        start, end = self._resolve_period(period, start_date, end_date)
        row = self.session.execute(
            select(
                func.count(OrderModel.id).label("total_orders"),
                func.coalesce(func.sum(case((OrderModel.status == OrderStatus.DELIVERED, 1), else_=0)), 0).label("delivered_orders"),
                func.coalesce(func.sum(case((OrderModel.status == OrderStatus.CANCELLED, 1), else_=0)), 0).label("cancelled_orders"),
                func.coalesce(func.sum(case((OrderModel.status == OrderStatus.PENDING, 1), else_=0)), 0).label("pending_orders"),
            ).where(and_(OrderModel.created_at >= start, OrderModel.created_at < end))
        ).one()
        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "total_orders": row.total_orders or 0,
            "delivered_orders": row.delivered_orders or 0,
            "cancelled_orders": row.cancelled_orders or 0,
            "pending_orders": row.pending_orders or 0,
            "top_selling_foods": self.top_selling_foods(limit=10, start=start, end=end),
            "top_customers": self.top_customers(limit=10, start=start, end=end),
        }

    def top_selling_foods(self, limit: int = 10, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        statement = (
            select(
                OrderItemModel.food_name_snapshot,
                func.sum(OrderItemModel.quantity).label("total_quantity"),
                func.coalesce(func.sum(OrderItemModel.subtotal), 0).label("revenue"),
            )
            .join(OrderModel, OrderItemModel.order_id == OrderModel.id)
            .group_by(OrderItemModel.food_name_snapshot)
            .order_by(desc("total_quantity"))
            .limit(limit)
        )
        if start and end:
            statement = statement.where(and_(OrderModel.created_at >= start, OrderModel.created_at < end))
        rows = self.session.execute(statement).all()
        return [
            {"food_name": row.food_name_snapshot, "total_quantity": int(row.total_quantity or 0), "revenue": row.revenue}
            for row in rows
        ]

    def top_customers(self, limit: int = 10, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        statement = (
            select(
                UserModel.id,
                UserModel.first_name,
                UserModel.last_name,
                func.count(OrderModel.id).label("total_orders"),
                func.coalesce(func.sum(OrderModel.total), 0).label("total_spent"),
            )
            .join(OrderModel, OrderModel.user_id == UserModel.id)
            .group_by(UserModel.id, UserModel.first_name, UserModel.last_name)
            .order_by(desc("total_spent"))
            .limit(limit)
        )
        if start and end:
            statement = statement.where(and_(OrderModel.created_at >= start, OrderModel.created_at < end))
        rows = self.session.execute(statement).all()
        return [
            {
                "user_id": row.id,
                "customer_name": f"{row.first_name} {row.last_name}",
                "total_orders": int(row.total_orders or 0),
                "total_spent": row.total_spent,
            }
            for row in rows
        ]

    def recent_orders(self, limit: int = 5) -> list[dict]:
        orders = self.session.scalars(select(OrderModel).order_by(OrderModel.created_at.desc()).limit(limit)).all()
        return [
            {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "total": order.total,
                "created_at": order.created_at,
            }
            for order in orders
        ]

    def _resolve_period(self, period: str | None, start_date: date | None, end_date: date | None) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == "weekly":
            start = now - timedelta(days=7)
            end = now + timedelta(seconds=1)
        elif period == "monthly":
            start = now - timedelta(days=30)
            end = now + timedelta(seconds=1)
        else:
            start = datetime.combine(start_date or now.date(), datetime.min.time(), tzinfo=UTC)
            end = datetime.combine((end_date or now.date()) + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        return start, end

    def _count(self, statement) -> int:
        return self.session.scalar(statement) or 0

    def _count_by_role(self, role: RoleName) -> int:
        return self.session.scalar(select(func.count()).select_from(UserModel).where(UserModel.role.has(name=role.value))) or 0

    def _count_orders_by_status(self, status: OrderStatus) -> int:
        return self.session.scalar(select(func.count()).select_from(OrderModel).where(OrderModel.status == status)) or 0

    def _revenue_between(self, start: datetime, end: datetime) -> Decimal:
        return self.session.scalar(
            select(func.coalesce(func.sum(PaymentModel.amount), 0)).where(
                PaymentModel.status == PaymentStatus.SUCCESSFUL,
                PaymentModel.paid_at.is_not(None),
                PaymentModel.paid_at >= start,
                PaymentModel.paid_at < end,
            )
        ) or Decimal("0.00")

    def _successful_payments_between(self, start: datetime, end: datetime) -> int:
        return self.session.scalar(
            select(func.count()).select_from(PaymentModel).where(
                PaymentModel.status == PaymentStatus.SUCCESSFUL,
                PaymentModel.paid_at.is_not(None),
                PaymentModel.paid_at >= start,
                PaymentModel.paid_at < end,
            )
        ) or 0

    def _average_order_value(self) -> Decimal:
        return self.session.scalar(
            select(func.coalesce(func.avg(OrderModel.total), 0)).where(OrderModel.payment_status == PaymentStatus.SUCCESSFUL)
        ) or Decimal("0.00")
