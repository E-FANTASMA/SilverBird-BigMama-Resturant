from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.delivery_service import DeliveryService
from app.dependencies.auth import get_current_user, require_roles
from app.dependencies.services import get_delivery_service
from app.domain.enums import RoleName
from app.schemas.delivery import DeliveryResponse, DeliveryStatusUpdateRequest

router = APIRouter(dependencies=[Depends(require_roles(RoleName.DELIVERY_PERSONNEL))])


@router.get("", response_model=list[DeliveryResponse])
def list_assigned_deliveries(
    current_user=Depends(get_current_user),
    service: DeliveryService = Depends(get_delivery_service),
):
    return service.list_assigned_deliveries(current_user.id)


@router.patch("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: UUID,
    payload: DeliveryStatusUpdateRequest,
    current_user=Depends(get_current_user),
    service: DeliveryService = Depends(get_delivery_service),
):
    return service.update_delivery_status(current_user.id, delivery_id, payload)
