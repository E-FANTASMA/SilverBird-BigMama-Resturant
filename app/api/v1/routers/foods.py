from uuid import UUID

from fastapi import APIRouter, Depends, File, Response, UploadFile

from app.application.services.food_service import FoodService
from app.dependencies.auth import get_current_user_optional, require_roles
from app.dependencies.services import get_food_service
from app.domain.enums import RoleName
from app.schemas.food import FoodCreateRequest, FoodResponse, FoodUpdateRequest

router = APIRouter()


@router.get("", response_model=list[FoodResponse])
def list_foods(
    current_user=Depends(get_current_user_optional),
    service: FoodService = Depends(get_food_service),
):
    include_unavailable = bool(current_user and current_user.role and current_user.role.name == RoleName.ADMIN)
    return service.list_foods(include_unavailable=include_unavailable)


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(
    food_id: UUID,
    current_user=Depends(get_current_user_optional),
    service: FoodService = Depends(get_food_service),
):
    include_unavailable = bool(current_user and current_user.role and current_user.role.name == RoleName.ADMIN)
    return service.get_food(food_id, include_unavailable=include_unavailable)


@router.post("", response_model=FoodResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def create_food(payload: FoodCreateRequest, service: FoodService = Depends(get_food_service)):
    return service.create_food(payload)


@router.patch("/{food_id}", response_model=FoodResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def update_food(food_id: UUID, payload: FoodUpdateRequest, service: FoodService = Depends(get_food_service)):
    return service.update_food(food_id, payload)


@router.delete("/{food_id}", status_code=204, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def delete_food(food_id: UUID, service: FoodService = Depends(get_food_service)):
    service.delete_food(food_id)
    return Response(status_code=204)


@router.post("/{food_id}/image", response_model=FoodResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
async def upload_food_image(
    food_id: UUID,
    image: UploadFile = File(...),
    service: FoodService = Depends(get_food_service),
):
    content = await image.read()
    return service.upload_food_image(
        food_id,
        filename=image.filename or "upload.bin",
        content_type=image.content_type,
        content=content,
    )
