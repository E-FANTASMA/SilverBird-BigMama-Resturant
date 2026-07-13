from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.order_service import OrderService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_order_service
from app.schemas.order import OrderCreateRequest, OrderResponse

router = APIRouter()


@router.post("", response_model=OrderResponse)
def create_order(
    payload: OrderCreateRequest,
    current_user=Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return service.create_order(current_user.id, payload)


@router.get("", response_model=list[OrderResponse])
def list_orders(current_user=Depends(get_current_user), service: OrderService = Depends(get_order_service)):
    return service.list_orders(current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, current_user=Depends(get_current_user), service: OrderService = Depends(get_order_service)):
    return service.get_order(order_id, user_id=current_user.id)
