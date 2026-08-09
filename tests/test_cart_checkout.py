from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.application.services.category_service import CategoryService
from app.application.services.food_service import FoodService
from app.core.security import create_access_token
from app.domain.enums import PaymentStatus, RoleName
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.models.user import UserModel


def seed_roles(session) -> None:
    for role_name in RoleName:
        session.add(RoleModel(name=role_name.value, description=role_name.value))
    session.commit()


def create_customer(session, email: str = "customer@example.com") -> str:
    customer_role = session.query(RoleModel).filter(RoleModel.name == RoleName.CUSTOMER.value).one()
    user = UserModel(
        role_id=customer_role.id,
        first_name="Test",
        last_name="Customer",
        email=email,
        phone="+2348077777777",
        password_hash="placeholder",
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return create_access_token(user.id, {"role": RoleName.CUSTOMER.value})


def test_cart_merges_duplicate_items_and_returns_totals(client, session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    token = create_customer(session)
    food = FoodService(session).list_foods()[0]

    response_one = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"food_item_id": str(food.id), "quantity": 2},
    )
    assert response_one.status_code == 200

    response_two = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"food_item_id": str(food.id), "quantity": 3},
    )
    assert response_two.status_code == 200
    payload = response_two.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["quantity"] == 5
    assert Decimal(payload["subtotal"]) == Decimal(food.price) * 5
    assert Decimal(payload["tax_amount"]) == Decimal("0")
    assert Decimal(payload["discount_amount"]) == Decimal("0")
    assert Decimal(payload["grand_total"]) >= Decimal(payload["subtotal"])


def test_customer_can_manage_addresses_and_default_flag(client, session) -> None:
    seed_roles(session)
    token = create_customer(session, email="address@example.com")

    home = client.post(
        "/api/v1/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address": "1 Admiralty Way",
            "city": "Lekki",
            "state": "Lagos",
            "phone": "+2348011111111",
            "latitude": 6.4698,
            "longitude": 3.5852,
            "is_default": True,
        },
    )
    assert home.status_code == 200
    assert home.json()["is_default"] is True

    office = client.post(
        "/api/v1/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Office",
            "address": "2 Ozumba Mbadiwe",
            "city": "Victoria Island",
            "state": "Lagos",
            "phone": "+2348022222222",
            "latitude": 6.4281,
            "longitude": 3.4219,
            "is_default": False,
        },
    )
    assert office.status_code == 200

    set_default = client.post(
        f"/api/v1/addresses/{office.json()['id']}/default",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert set_default.status_code == 200
    assert set_default.json()["is_default"] is True

    listed = client.get("/api/v1/addresses", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == office.json()["id"]


def test_checkout_creates_delivery_order_and_clears_cart(client, session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    token = create_customer(session, email="checkout@example.com")
    food = FoodService(session).list_foods()[0]

    address = client.post(
        "/api/v1/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address": "5 Bourdillon Road",
            "city": "Ikoyi",
            "state": "Lagos",
            "phone": "+2348033333333",
            "latitude": 6.4549,
            "longitude": 3.4310,
            "is_default": True,
        },
    )
    assert address.status_code == 200

    add_item = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"food_item_id": str(food.id), "quantity": 2},
    )
    assert add_item.status_code == 200

    create_order = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_type": "DELIVERY", "delivery_address_id": address.json()["id"]},
    )
    assert create_order.status_code == 200
    order_payload = create_order.json()
    assert order_payload["order_number"].startswith("SBBM-")
    assert order_payload["delivery_address_id"] == address.json()["id"]
    assert Decimal(order_payload["delivery_fee"]) > Decimal("0")
    assert len(order_payload["items"]) == 1

    cart = client.get("/api/v1/cart", headers={"Authorization": f"Bearer {token}"})
    assert cart.status_code == 200
    assert cart.json()["items"] == []
    assert cart.json()["grand_total"] == "0.00"


def test_pickup_requires_future_time(client, session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    token = create_customer(session, email="pickup@example.com")
    food = FoodService(session).list_foods()[0]

    client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"food_item_id": str(food.id), "quantity": 1},
    )
    response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_type": "PICKUP", "scheduled_pickup_time": datetime.now(UTC).isoformat()},
    )
    assert response.status_code == 422

    future_response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_type": "PICKUP", "scheduled_pickup_time": (datetime.now(UTC) + timedelta(hours=1)).isoformat()},
    )
    assert future_response.status_code == 200


def test_payment_verify_is_idempotent(client, session, monkeypatch) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    token = create_customer(session, email="payment@example.com")
    food = FoodService(session).list_foods()[0]

    client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"food_item_id": str(food.id), "quantity": 1},
    )
    order_response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_type": "DINE_IN", "table_number": "A12"},
    )
    order_id = order_response.json()["id"]

    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._initialize_paystack_transaction",
        lambda self, **kwargs: "https://checkout.paystack.test/abc123",
    )
    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._verify_paystack_transaction",
        lambda self, reference: {"status": "success", "gateway_response": "Approved", "channel": "card"},
    )

    initialized = client.post(
        "/api/v1/payments/initialize",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_id": order_id},
    )
    assert initialized.status_code == 200
    reference = initialized.json()["reference"]

    first_verify = client.get(f"/api/v1/payments/verify/{reference}", headers={"Authorization": f"Bearer {token}"})
    assert first_verify.status_code == 200
    assert first_verify.json()["status"] == PaymentStatus.SUCCESSFUL.value

    second_verify = client.get(f"/api/v1/payments/verify/{reference}", headers={"Authorization": f"Bearer {token}"})
    assert second_verify.status_code == 200
    assert second_verify.json()["status"] == PaymentStatus.SUCCESSFUL.value
