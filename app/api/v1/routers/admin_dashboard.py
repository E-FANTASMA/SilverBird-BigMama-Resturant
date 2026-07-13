from fastapi import APIRouter, Depends

from app.application.services.report_service import ReportService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_report_service
from app.domain.enums import RoleName

router = APIRouter(dependencies=[Depends(require_roles(RoleName.ADMIN))])


@router.get("")
def get_dashboard(service: ReportService = Depends(get_report_service)):
    return service.dashboard_summary()
