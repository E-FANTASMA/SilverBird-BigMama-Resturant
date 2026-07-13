from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.dependencies.auth import get_current_user
from app.infrastructure.database.models.address import DeliveryAddressModel
from app.infrastructure.database.repositories.address_repository import AddressRepository
from app.infrastructure.database.session import get_db_session
from app.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest

router = APIRouter()


@router.get("", response_model=list[AddressResponse])
def list_addresses(current_user=Depends(get_current_user), session: Session = Depends(get_db_session)):
    return AddressRepository(session).list_by_user_id(current_user.id)


@router.post("", response_model=AddressResponse)
def create_address(
    payload: AddressCreateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    address = DeliveryAddressModel(user_id=current_user.id, **payload.model_dump())
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: UUID,
    payload: AddressUpdateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    address = AddressRepository(session).get(address_id)
    if str(address.user_id) != str(current_user.id):
        raise ForbiddenException("You do not have access to this address")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
    session.commit()
    session.refresh(address)
    return address
