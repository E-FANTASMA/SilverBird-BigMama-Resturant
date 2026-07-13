from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.category_service import CategoryService
from app.dependencies.auth import require_roles
from app.dependencies.services import get_category_service
from app.domain.enums import RoleName
from app.schemas.category import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest

router = APIRouter()


@router.get("", response_model=list[CategoryResponse])
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()


@router.post("", response_model=CategoryResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def create_category(payload: CategoryCreateRequest, service: CategoryService = Depends(get_category_service)):
    return service.create_category(payload)


@router.patch("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(require_roles(RoleName.ADMIN))])
def update_category(category_id: UUID, payload: CategoryUpdateRequest, service: CategoryService = Depends(get_category_service)):
    return service.update_category(category_id, payload)
