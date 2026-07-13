from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.delivery_service import DeliveryService
from app.application.services.order_service import OrderService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_delivery_service, get_order_service
from app.domain.enums import RoleName
from app.schemas.delivery import DeliveryAssignRequest, DeliveryResponse
from app.schemas.order import OrderResponse

router = APIRouter(dependencies=[Depends(require_roles(RoleName.ADMIN))])


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, service: OrderService = Depends(get_order_service)):
    return service.get_order(order_id)


@router.post("/{order_id}/assign-delivery", response_model=DeliveryResponse)
def assign_delivery(order_id: UUID, payload: DeliveryAssignRequest, service: DeliveryService = Depends(get_delivery_service)):
    return service.assign_delivery(order_id, payload)
