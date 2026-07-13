from fastapi import APIRouter, Depends

from app.application.services.notification_service import NotificationService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_notification_service
from app.schemas.notification import NotificationCreateRequest, NotificationResponse

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
def list_notifications(current_user=Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return service.list_notifications(current_user.id)


@router.post("", response_model=NotificationResponse)
def create_notification(payload: NotificationCreateRequest, service: NotificationService = Depends(get_notification_service)):
    return service.create_notification(payload)
