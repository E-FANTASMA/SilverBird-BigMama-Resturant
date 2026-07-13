from fastapi import APIRouter, Depends

from app.application.services.user_service import UserService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_user_service
from app.schemas.user import ProfileUpdateRequest, UserResponse

router = APIRouter()


@router.get("", response_model=UserResponse)
def get_profile(current_user=Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return service.get_profile(current_user.id)


@router.patch("", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.update_profile(current_user.id, payload)
