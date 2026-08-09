from app.core.security import create_access_token
from app.domain.enums import RoleName
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.models.user import UserModel


def seed_roles(session) -> None:
    for role_name in RoleName:
        session.add(RoleModel(name=role_name.value, description=role_name.value))
    session.commit()


def test_customer_signup_and_login_flow(client, session) -> None:
    seed_roles(session)

    signup_payload = {
        "first_name": "Ada",
        "last_name": "Obi",
        "email": "ada@example.com",
        "phone": "+2348012345678",
        "password": "StrongPass1!",
    }
    signup_response = client.post("/api/v1/auth/signup", json=signup_payload)

    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert signup_data["token_type"] == "bearer"
    assert signup_data["access_token"]
    assert signup_data["refresh_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": signup_payload["email"], "password": signup_payload["password"]},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_signup_rejects_weak_password(client, session) -> None:
    seed_roles(session)

    response = client.post(
        "/api/v1/auth/signup",
        json={
            "first_name": "Tola",
            "last_name": "Ade",
            "email": "tola@example.com",
            "phone": "+2348099999999",
            "password": "weakpass",
        },
    )

    assert response.status_code == 422


def test_refresh_and_logout_revoke_refresh_token(client, session) -> None:
    seed_roles(session)
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "first_name": "Musa",
            "last_name": "Danjuma",
            "email": "musa@example.com",
            "phone": "+2348022222222",
            "password": "Another1!",
        },
    )
    original_refresh_token = signup_response.json()["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": original_refresh_token})
    assert refresh_response.status_code == 200
    rotated_refresh_token = refresh_response.json()["refresh_token"]
    assert rotated_refresh_token != original_refresh_token

    logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": rotated_refresh_token})
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logout successful"

    revoked_refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": rotated_refresh_token})
    assert revoked_refresh_response.status_code == 401


def test_forgot_and_reset_password_flow(client, session) -> None:
    seed_roles(session)
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "first_name": "Bola",
            "last_name": "Khan",
            "email": "bola@example.com",
            "phone": "+2348033333333",
            "password": "Original1!",
        },
    )
    assert signup_response.status_code == 200

    forgot_response = client.post("/api/v1/auth/forgot-password", json={"email": "bola@example.com"})
    assert forgot_response.status_code == 200
    reset_token = forgot_response.json()["reset_token"]
    assert reset_token

    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": reset_token,
            "password": "Updated1!",
            "confirm_password": "Updated1!",
        },
    )
    assert reset_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "bola@example.com", "password": "Updated1!"},
    )
    assert login_response.status_code == 200


def test_admin_can_create_privileged_users(client, session) -> None:
    seed_roles(session)
    admin_signup = client.post(
        "/api/v1/auth/signup",
        json={
            "first_name": "Grace",
            "last_name": "Admin",
            "email": "grace@example.com",
            "phone": "+2348044444444",
            "password": "AdminPass1!",
        },
    )
    admin_user_id = session.query(RoleModel).filter(RoleModel.name == RoleName.ADMIN.value).one().id
    user = session.query(UserModel).filter_by(email="grace@example.com").one()
    user.role_id = admin_user_id
    session.commit()
    admin_token = create_access_token(user.id, {"role": RoleName.ADMIN.value})

    response = client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "role": RoleName.DELIVERY_PERSONNEL.value,
            "first_name": "David",
            "last_name": "Rider",
            "email": "david@example.com",
            "phone": "+2348055555555",
            "password": "Delivery1!",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "david@example.com"
