import hashlib
import hmac
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from app.application.services.notification_service import NotificationService
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceException, ForbiddenException, NotFoundException, ValidationException
from app.core.logging import get_logger, log_event
from app.domain.enums import OrderStatus, PaymentStatus
from app.infrastructure.database.models.payment import PaymentModel, PaymentWebhookEventModel
from app.infrastructure.database.repositories.order_repository import OrderRepository
from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentVerifyResponse,
    PaystackWebhookRequest,
)


class PaymentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.orders = OrderRepository(session)
        self.payments = PaymentRepository(session)
        self.notifications = NotificationService(session)

    def initialize_payment(self, payload: PaymentInitializeRequest, user_id=None, is_admin: bool = False) -> PaymentInitializeResponse:
        order_id = payload.order_id
        order = self.orders.get(order_id)
        if not is_admin and user_id is not None and str(order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this order")
        if order.payment_status == PaymentStatus.SUCCESSFUL:
            raise ValidationException("Order has already been paid")

        reference = f"paystack_{uuid4().hex}"
        authorization_url = self._initialize_paystack_transaction(reference=reference, amount=Decimal(order.total), email=order.user.email)
        payment = PaymentModel(
            order_id=order.id,
            reference=reference,
            amount=Decimal(order.total),
            status=PaymentStatus.PENDING,
        )
        self.session.add(payment)
        self.session.commit()
        log_event(logger, "payment_initialized", order_id=order.id, payment_reference=reference, amount=order.total)
        return PaymentInitializeResponse(
            order_id=order.id,
            reference=reference,
            authorization_url=authorization_url,
            amount=order.total,
            status=payment.status,
        )

    def verify_payment(self, reference: str, user_id=None, is_admin: bool = False) -> PaymentVerifyResponse:
        payment = self.payments.get_by_reference(reference)
        if not payment:
            raise NotFoundException("Payment reference not found")
        if not is_admin and user_id is not None and str(payment.order.user_id) != str(user_id):
            raise ForbiddenException("You do not have access to this payment")
        if payment.status == PaymentStatus.SUCCESSFUL:
            return PaymentVerifyResponse(
                order_id=payment.order_id,
                reference=payment.reference,
                status=payment.status,
                gateway_response=payment.gateway_response,
                paid_at=payment.paid_at,
            )

        verification = self._verify_paystack_transaction(reference)
        status = str(verification.get("status", "")).lower()
        gateway_response = verification.get("gateway_response") or verification.get("message")
        channel = verification.get("channel")

        payment.payment_method = channel
        payment.gateway_response = gateway_response
        if status == "success":
            payment.status = PaymentStatus.SUCCESSFUL
            payment.paid_at = datetime.now(UTC)
            payment.order.payment_status = PaymentStatus.SUCCESSFUL
            if payment.order.status == OrderStatus.PENDING:
                payment.order.status = OrderStatus.CONFIRMED
            self.notifications.create_payment_notification(
                payment.order.user_id,
                "Payment Successful",
                f"Payment for order {payment.order.order_number} was confirmed successfully.",
            )
        else:
            payment.status = PaymentStatus.FAILED
            payment.order.payment_status = PaymentStatus.FAILED
        self.session.commit()
        log_event(
            logger,
            "payment_verified",
            order_id=payment.order_id,
            payment_reference=payment.reference,
            payment_status=payment.status,
        )
        return PaymentVerifyResponse(
            order_id=payment.order_id,
            reference=payment.reference,
            status=payment.status,
            gateway_response=payment.gateway_response,
            paid_at=payment.paid_at,
        )

    def handle_webhook(self, payload: PaystackWebhookRequest, signature: str | None) -> dict[str, str]:
        self._validate_paystack_signature(payload.model_dump(), signature)
        reference = payload.data.get("reference")
        event = PaymentWebhookEventModel(
            provider="PAYSTACK",
            event_type=payload.event,
            reference=reference,
            payload=payload.model_dump(),
            signature=signature,
            processed=False,
        )
        self.session.add(event)
        self.session.flush()

        if payload.event == "charge.success" and reference:
            payment = self.payments.get_by_reference(reference)
            if payment and payment.status != PaymentStatus.SUCCESSFUL:
                payment.status = PaymentStatus.SUCCESSFUL
                payment.paid_at = datetime.now(UTC)
                payment.gateway_response = payload.data.get("gateway_response") or "Webhook confirmed"
                payment.payment_method = payload.data.get("channel")
                payment.order.payment_status = PaymentStatus.SUCCESSFUL
                if payment.order.status == OrderStatus.PENDING:
                    payment.order.status = OrderStatus.CONFIRMED
                self.notifications.create_payment_notification(
                    payment.order.user_id,
                    "Payment Successful",
                    f"Payment for order {payment.order.order_number} was confirmed successfully.",
                )

        event.processed = True
        event.processed_at = datetime.now(UTC)
        self.session.commit()
        log_event(logger, "payment_webhook_processed", reference=reference, event_type=payload.event)
        return {"message": "Webhook processed successfully"}

    def _initialize_paystack_transaction(self, *, reference: str, amount: Decimal, email: str) -> str:
        payload = {
            "reference": reference,
            "amount": int((amount * 100).quantize(Decimal("1"))),
            "email": email,
            "currency": "NGN",
        }
        data = self._paystack_request("POST", "/transaction/initialize", json=payload)
        authorization_url = data.get("authorization_url")
        if not authorization_url:
            raise ExternalServiceException("Paystack did not return an authorization URL")
        return authorization_url

    def _verify_paystack_transaction(self, reference: str) -> dict:
        data = self._paystack_request("GET", f"/transaction/verify/{reference}")
        return data

    def _paystack_request(self, method: str, path: str, json: dict | None = None) -> dict:
        if not self.settings.paystack_secret_key or self.settings.paystack_secret_key == "paystack-secret":
            raise ExternalServiceException("Paystack secret key is not configured")
        headers = {"Authorization": f"Bearer {self.settings.paystack_secret_key}"}
        url = f"{self.settings.paystack_base_url}{path}"
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.request(method, url, json=json, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceException("Paystack request failed") from exc

        payload = response.json()
        if not payload.get("status"):
            raise ExternalServiceException(payload.get("message") or "Paystack request was unsuccessful")
        return payload.get("data", {})

    def _validate_paystack_signature(self, payload: dict, signature: str | None) -> None:
        if not self.settings.paystack_webhook_secret or self.settings.paystack_webhook_secret == "paystack-webhook-secret":
            raise ExternalServiceException("Paystack webhook secret is not configured")
        if not signature:
            raise ValidationException("Missing Paystack signature")
        import json

        digest = hmac.new(
            self.settings.paystack_webhook_secret.encode("utf-8"),
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(digest, signature):
            raise ValidationException("Invalid Paystack signature")


logger = get_logger(__name__)
