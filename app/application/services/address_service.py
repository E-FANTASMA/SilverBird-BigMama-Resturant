from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.infrastructure.database.models.address import DeliveryAddressModel
from app.infrastructure.database.repositories.address_repository import AddressRepository
from app.schemas.address import AddressCreateRequest, AddressUpdateRequest


class AddressService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.addresses = AddressRepository(session)

    def list_addresses(self, user_id):
        return self.addresses.list_by_user_id(user_id)

    def create_address(self, user_id, payload: AddressCreateRequest):
        should_be_default = payload.is_default or not self.addresses.list_by_user_id(user_id)
        if should_be_default:
            self.addresses.clear_default_for_user(user_id)

        address = DeliveryAddressModel(
            user_id=user_id,
            label=payload.label.strip(),
            address=payload.address.strip(),
            city=payload.city.strip(),
            state=payload.state.strip(),
            phone=payload.phone,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_default=should_be_default,
        )
        self.session.add(address)
        self.session.commit()
        self.session.refresh(address)
        return address

    def update_address(self, user_id, address_id, payload: AddressUpdateRequest):
        address = self._get_owned_address(user_id, address_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "is_default" in update_data and update_data["is_default"]:
            self.addresses.clear_default_for_user(user_id)

        for field, value in update_data.items():
            if isinstance(value, str):
                value = value.strip()
            setattr(address, field, value)

        if not address.is_default:
            default_address = self.addresses.get_default_by_user_id(user_id)
            if not default_address:
                address.is_default = True

        self.session.commit()
        self.session.refresh(address)
        return address

    def delete_address(self, user_id, address_id) -> None:
        address = self._get_owned_address(user_id, address_id)
        address.deleted_at = datetime.now(UTC)
        address.is_default = False

        remaining = [entry for entry in self.addresses.list_by_user_id(user_id) if entry.id != address.id]
        if remaining and not any(entry.is_default for entry in remaining):
            remaining[0].is_default = True

        self.session.commit()

    def set_default_address(self, user_id, address_id):
        address = self._get_owned_address(user_id, address_id)
        self.addresses.clear_default_for_user(user_id)
        address.is_default = True
        self.session.commit()
        self.session.refresh(address)
        return address

    def get_default_address(self, user_id):
        return self.addresses.get_default_by_user_id(user_id)

    def validate_delivery_address(self, user_id, address_id):
        return self._get_owned_address(user_id, address_id)

    def _get_owned_address(self, user_id, address_id):
        address = self.addresses.get_by_user_id_and_id(user_id, address_id)
        if not address:
            owned_elsewhere = self.addresses.get(address_id)
            if str(owned_elsewhere.user_id) != str(user_id):
                raise ForbiddenException("You do not have access to this address")
            raise NotFoundException("Address not found")
        return address
