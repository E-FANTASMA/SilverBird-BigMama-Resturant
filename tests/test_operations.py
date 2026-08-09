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


def create_user_with_role(session, *, role: RoleName, email: str, phone: str) -> UserModel:
    role_model = session.query(RoleModel).filter(RoleModel.name == role.value).one()
    user = UserModel(
        role_id=role_model.id,
        first_name=role.value.title(),
        last_name="User",
        email=email,
        phone=phone,
        password_hash="placeholder",
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_token(user: UserModel, role: RoleName) -> str:
    return create_access_token(user.id, {"role": role.value})


def create_paid_delivery_order(client, session, customer_token: str):
    food = FoodService(session).list_foods()[0]
    address_response = client.post(
        "/api/v1/addresses",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "label": "Home",
            "address": "20 Marina",
            "city": "Lagos",
            "state": "Lagos",
            "phone": "+2348015555555",
            "latitude": 6.4550,
            "longitude": 3.3841,
            "is_default": True,
        },
    )
    client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"food_item_id": str(food.id), "quantity": 1},
    )
    address_id = address_response.json()["id"]
    order = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"order_type": "DELIVERY", "delivery_address_id": address_id},
    ).json()
    return order, address_id


def test_notifications_can_be_counted_and_marked_read(client, session) -> None:
    seed_roles(session)
    customer = create_user_with_role(
        session, role=RoleName.CUSTOMER, email="notice@example.com", phone="+2348011111000"
    )
    token = create_token(customer, RoleName.CUSTOMER)

    created = client.post(
        "/api/v1/notifications",
        json={
            "user_id": str(customer.id),
            "title": "Order Created",
            "message": "Your order is pending confirmation.",
            "type": "ORDER",
            "email_recipient": "notice@example.com",
        },
    )
    assert created.status_code == 200
    notification_id = created.json()["id"]
    assert len(created.json()["deliveries"]) == 1

    unread = client.get("/api/v1/notifications/unread-count", headers={"Authorization": f"Bearer {token}"})
    assert unread.status_code == 200
    assert unread.json()["unread_count"] == 1

    marked = client.patch(f"/api/v1/notifications/{notification_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True


def test_delivery_personnel_can_progress_delivery_and_get_contact(client, session, monkeypatch) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    customer = create_user_with_role(session, role=RoleName.CUSTOMER, email="ops-customer@example.com", phone="+2348012222000")
    admin = create_user_with_role(session, role=RoleName.ADMIN, email="ops-admin@example.com", phone="+2348013333000")
    rider = create_user_with_role(session, role=RoleName.DELIVERY_PERSONNEL, email="ops-rider@example.com", phone="+2348014444000")
    customer_token = create_token(customer, RoleName.CUSTOMER)
    admin_token = create_token(admin, RoleName.ADMIN)
    rider_token = create_token(rider, RoleName.DELIVERY_PERSONNEL)

    order, address_id = create_paid_delivery_order(client, session, customer_token)

    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._initialize_paystack_transaction",
        lambda self, **kwargs: "https://checkout.paystack.test/ops",
    )
    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._verify_paystack_transaction",
        lambda self, reference: {"status": "success", "gateway_response": "Approved", "channel": "card"},
    )

    initialized = client.post(
        "/api/v1/payments/initialize",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"order_id": order["id"]},
    )
    reference = initialized.json()["reference"]
    verified = client.get(f"/api/v1/payments/verify/{reference}", headers={"Authorization": f"Bearer {customer_token}"})
    assert verified.status_code == 200
    assert verified.json()["status"] == PaymentStatus.SUCCESSFUL.value

    assigned = client.post(
        f"/api/v1/admin/orders/{order['id']}/assign-delivery",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"delivery_personnel_id": str(rider.id), "delivery_address_id": address_id},
    )
    assert assigned.status_code == 200
    delivery_id = assigned.json()["id"]

    contact = client.get(f"/api/v1/delivery/orders/{delivery_id}/contact", headers={"Authorization": f"Bearer {rider_token}"})
    assert contact.status_code == 200
    assert contact.json()["customer_phone"] == customer.phone

    picked_up = client.patch(
        f"/api/v1/delivery/orders/{delivery_id}",
        headers={"Authorization": f"Bearer {rider_token}"},
        json={"status": "PICKED_UP"},
    )
    assert picked_up.status_code == 200

    in_transit = client.patch(
        f"/api/v1/delivery/orders/{delivery_id}",
        headers={"Authorization": f"Bearer {rider_token}"},
        json={"status": "IN_TRANSIT"},
    )
    assert in_transit.status_code == 200

    delivered = client.patch(
        f"/api/v1/delivery/orders/{delivery_id}",
        headers={"Authorization": f"Bearer {rider_token}"},
        json={"status": "DELIVERED"},
    )
    assert delivered.status_code == 200
    assert delivered.json()["status"] == "DELIVERED"


def test_admin_dashboard_and_reports_return_metrics(client, session, monkeypatch) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    customer = create_user_with_role(session, role=RoleName.CUSTOMER, email="metrics-customer@example.com", phone="+2348015555000")
    admin = create_user_with_role(session, role=RoleName.ADMIN, email="metrics-admin@example.com", phone="+2348016666000")
    customer_token = create_token(customer, RoleName.CUSTOMER)
    admin_token = create_token(admin, RoleName.ADMIN)

    order, _ = create_paid_delivery_order(client, session, customer_token)
    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._initialize_paystack_transaction",
        lambda self, **kwargs: "https://checkout.paystack.test/report",
    )
    monkeypatch.setattr(
        "app.application.services.payment_service.PaymentService._verify_paystack_transaction",
        lambda self, reference: {"status": "success", "gateway_response": "Approved", "channel": "card"},
    )
    initialized = client.post(
        "/api/v1/payments/initialize",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"order_id": order["id"]},
    )
    client.get(f"/api/v1/payments/verify/{initialized.json()['reference']}", headers={"Authorization": f"Bearer {customer_token}"})

    dashboard = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert dashboard.status_code == 200
    assert dashboard.json()["total_orders"] >= 1
    assert "top_selling_foods" in dashboard.json()

    revenue = client.get("/api/v1/admin/reports/revenue?period=daily", headers={"Authorization": f"Bearer {admin_token}"})
    assert revenue.status_code == 200
    assert "revenue" in revenue.json()

    orders = client.get("/api/v1/admin/reports/orders?period=daily", headers={"Authorization": f"Bearer {admin_token}"})
    assert orders.status_code == 200
    assert "top_customers" in orders.json()
