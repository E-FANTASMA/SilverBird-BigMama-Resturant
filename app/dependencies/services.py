from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.cart_service import CartService
from app.application.services.category_service import CategoryService
from app.application.services.delivery_service import DeliveryService
from app.application.services.food_service import FoodService
from app.application.services.notification_service import NotificationService
from app.application.services.order_service import OrderService
from app.application.services.payment_service import PaymentService
from app.application.services.pricing_service import OrderPricingService
from app.application.services.report_service import ReportService
from app.application.services.user_service import UserService
from app.core.config import get_settings
from app.infrastructure.database.session import get_db_session


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(session)


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    return UserService(session)


def get_category_service(session: Session = Depends(get_db_session)) -> CategoryService:
    return CategoryService(session)


def get_food_service(session: Session = Depends(get_db_session)) -> FoodService:
    return FoodService(session)


def get_cart_service(session: Session = Depends(get_db_session)) -> CartService:
    return CartService(session)


def get_order_service(session: Session = Depends(get_db_session)) -> OrderService:
    return OrderService(session, OrderPricingService(get_settings()))


def get_payment_service(session: Session = Depends(get_db_session)) -> PaymentService:
    return PaymentService(session)


def get_delivery_service(session: Session = Depends(get_db_session)) -> DeliveryService:
    return DeliveryService(session)


def get_notification_service(session: Session = Depends(get_db_session)) -> NotificationService:
    return NotificationService(session)


def get_report_service(session: Session = Depends(get_db_session)) -> ReportService:
    return ReportService(session)
