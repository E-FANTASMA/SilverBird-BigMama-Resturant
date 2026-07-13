from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.order import OrderModel
from app.infrastructure.database.models.user import UserModel


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def dashboard_summary(self) -> dict[str, int | Decimal]:
        total_users = self.session.scalar(select(func.count()).select_from(UserModel)) or 0
        total_orders = self.session.scalar(select(func.count()).select_from(OrderModel)) or 0
        revenue = self.session.scalar(select(func.coalesce(func.sum(OrderModel.total), 0)).select_from(OrderModel)) or Decimal("0.00")
        return {"total_users": total_users, "total_orders": total_orders, "revenue": revenue}
