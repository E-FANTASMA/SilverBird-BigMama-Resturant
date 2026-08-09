from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from app.application.services.payment_service import PaymentService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_payment_service
from app.schemas.payment import PaymentInitializeRequest, PaymentInitializeResponse, PaymentVerifyResponse, PaystackWebhookRequest

router = APIRouter()


@router.post("/initialize", response_model=PaymentInitializeResponse)
def initialize_payment(
    payload: PaymentInitializeRequest,
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    return service.initialize_payment(payload, user_id=current_user.id)


@router.post("/paystack/initialize", response_model=PaymentInitializeResponse, include_in_schema=False)
def initialize_payment_legacy(
    order_id: UUID = Query(...),
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    return service.initialize_payment(PaymentInitializeRequest(order_id=order_id), user_id=current_user.id)


@router.get("/verify/{reference}", response_model=PaymentVerifyResponse)
def verify_payment(reference: str, current_user=Depends(get_current_user), service: PaymentService = Depends(get_payment_service)):
    return service.verify_payment(reference, user_id=current_user.id)


@router.get("/paystack/verify/{reference}", response_model=PaymentVerifyResponse, include_in_schema=False)
def verify_payment_legacy(
    reference: str,
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    return service.verify_payment(reference, user_id=current_user.id)


@router.post("/webhook")
def paystack_webhook(
    payload: PaystackWebhookRequest,
    service: PaymentService = Depends(get_payment_service),
    x_paystack_signature: str | None = Header(default=None),
) -> dict[str, str]:
    return service.handle_webhook(payload, x_paystack_signature)
