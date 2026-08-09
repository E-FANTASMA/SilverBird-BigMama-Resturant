from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.services.notification_service import NotificationService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_notification_service
from app.schemas.notification import NotificationCreateRequest, NotificationResponse, NotificationUnreadCountResponse

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
def list_notifications(current_user=Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return service.list_notifications(current_user.id)


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def get_unread_count(current_user=Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return NotificationUnreadCountResponse(unread_count=service.get_unread_count(current_user.id))


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: UUID,
    current_user=Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    return service.mark_as_read(current_user.id, notification_id)


@router.patch("/read-all")
def mark_all_as_read(current_user=Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return service.mark_all_as_read(current_user.id)


@router.post("", response_model=NotificationResponse)
def create_notification(payload: NotificationCreateRequest, service: NotificationService = Depends(get_notification_service)):
    return service.create_notification(payload)
