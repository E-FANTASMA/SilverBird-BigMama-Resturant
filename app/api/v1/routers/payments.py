from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.services.payment_service import PaymentService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_payment_service
from app.schemas.payment import PaymentInitializeResponse, PaymentVerifyResponse

router = APIRouter()


@router.post("/paystack/initialize", response_model=PaymentInitializeResponse)
def initialize_payment(
    order_id: UUID = Query(...),
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    return service.initialize_payment(order_id, user_id=current_user.id)


@router.get("/paystack/verify/{reference}", response_model=PaymentVerifyResponse)
def verify_payment(reference: str, current_user=Depends(get_current_user), service: PaymentService = Depends(get_payment_service)):
    return service.verify_payment(reference, user_id=current_user.id)


@router.post("/webhook")
def paystack_webhook() -> dict[str, str]:
    return {"message": "Webhook endpoint reserved for Paystack callbacks."}
