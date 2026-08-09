from collections.abc import Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.dependencies.services import get_auth_service
from app.infrastructure.database.models.address import DeliveryAddressModel
from app.infrastructure.database.models.category import CategoryModel
from app.infrastructure.database.models.cart import CartModel
from app.infrastructure.database.models.cart import CartItemModel
from app.infrastructure.database.models.delivery import DeliveryModel
from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.models.notification import NotificationDeliveryModel, NotificationModel
from app.infrastructure.database.models.order import OrderItemModel, OrderModel
from app.infrastructure.database.models.payment import PaymentModel, PaymentWebhookEventModel
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.models.token import PasswordResetTokenModel, RefreshTokenModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.session import get_db_session
from app.main import app


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        RoleModel.__table__,
        UserModel.__table__,
        CartModel.__table__,
        CartItemModel.__table__,
        RefreshTokenModel.__table__,
        PasswordResetTokenModel.__table__,
        CategoryModel.__table__,
        FoodItemModel.__table__,
        DeliveryAddressModel.__table__,
        OrderModel.__table__,
        OrderItemModel.__table__,
        PaymentModel.__table__,
        PaymentWebhookEventModel.__table__,
        DeliveryModel.__table__,
        NotificationModel.__table__,
        NotificationDeliveryModel.__table__,
    ]
    for table in tables:
        table.create(bind=engine)

    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides.pop(get_auth_service, None)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
