from datetime import date

from fastapi import APIRouter, Depends, Query

from app.application.services.report_service import ReportService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_report_service
from app.domain.enums import RoleName

router = APIRouter(dependencies=[Depends(require_roles(RoleName.ADMIN))])


@router.get("/revenue")
def revenue_report(
    period: str | None = Query(default=None, pattern="^(daily|weekly|monthly)$"),
    start_date: date | None = None,
    end_date: date | None = None,
    service: ReportService = Depends(get_report_service),
):
    return service.revenue_report(period=period, start_date=start_date, end_date=end_date)


@router.get("/orders")
def order_report(
    period: str | None = Query(default=None, pattern="^(daily|weekly|monthly)$"),
    start_date: date | None = None,
    end_date: date | None = None,
    service: ReportService = Depends(get_report_service),
):
    return service.orders_report(period=period, start_date=start_date, end_date=end_date)
