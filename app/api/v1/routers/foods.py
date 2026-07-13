from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.food_service import FoodService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_food_service
from app.domain.enums import RoleName
from app.schemas.food import FoodCreateRequest, FoodResponse, FoodUpdateRequest

router = APIRouter()


@router.get("", response_model=list[FoodResponse])
def list_foods(service: FoodService = Depends(get_food_service)):
    return service.list_foods()


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(food_id: UUID, service: FoodService = Depends(get_food_service)):
    return service.get_food(food_id)


@router.post("", response_model=FoodResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def create_food(payload: FoodCreateRequest, service: FoodService = Depends(get_food_service)):
    return service.create_food(payload)


@router.patch("/{food_id}", response_model=FoodResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def update_food(food_id: UUID, payload: FoodUpdateRequest, service: FoodService = Depends(get_food_service)):
    return service.update_food(food_id, payload)
