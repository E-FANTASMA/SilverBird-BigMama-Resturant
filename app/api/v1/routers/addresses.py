from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.services.address_service import AddressService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_address_service
from app.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest

router = APIRouter()


@router.get("", response_model=list[AddressResponse])
def list_addresses(current_user=Depends(get_current_user), service: AddressService = Depends(get_address_service)):
    return service.list_addresses(current_user.id)


@router.post("", response_model=AddressResponse)
def create_address(
    payload: AddressCreateRequest,
    current_user=Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    return service.create_address(current_user.id, payload)


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: UUID,
    payload: AddressUpdateRequest,
    current_user=Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    return service.update_address(current_user.id, address_id, payload)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: UUID,
    current_user=Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    service.delete_address(current_user.id, address_id)


@router.post("/{address_id}/default", response_model=AddressResponse)
def set_default_address(
    address_id: UUID,
    current_user=Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    return service.set_default_address(current_user.id, address_id)
