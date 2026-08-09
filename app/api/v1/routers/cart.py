from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.cart_service import CartService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_cart_service
from app.schemas.cart import CartItemCreateRequest, CartItemUpdateRequest, CartResponse

router = APIRouter()


@router.get("", response_model=CartResponse)
def get_cart(current_user=Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.get_cart(current_user.id)


@router.post("/items", response_model=CartResponse)
def add_item(
    payload: CartItemCreateRequest,
    current_user=Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(current_user.id, payload)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: UUID,
    payload: CartItemUpdateRequest,
    current_user=Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return service.update_item(current_user.id, item_id, payload)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: UUID, current_user=Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.remove_item(current_user.id, item_id)


@router.delete("", response_model=CartResponse)
def clear_cart(current_user=Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.clear_cart(current_user.id)
