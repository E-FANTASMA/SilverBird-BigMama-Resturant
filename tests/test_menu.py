from io import BytesIO

from app.application.services.category_service import CategoryService
from app.application.services.food_service import FoodService
from app.core.security import create_access_token
from app.domain.enums import RoleName
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.supabase_storage import StoredImage


def seed_roles(session) -> None:
    for role_name in RoleName:
        session.add(RoleModel(name=role_name.value, description=role_name.value))
    session.commit()


def seed_admin(session) -> str:
    admin_role = session.query(RoleModel).filter(RoleModel.name == RoleName.ADMIN.value).one()
    admin = UserModel(
        role_id=admin_role.id,
        first_name="Menu",
        last_name="Admin",
        email="menu-admin@example.com",
        phone="+2348066666666",
        password_hash="placeholder",
        is_verified=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return create_access_token(admin.id, {"role": RoleName.ADMIN.value})


def test_default_categories_and_menu_seed(session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()

    categories = CategoryService(session).list_categories()
    foods = FoodService(session).list_foods()

    assert [category.name for category in categories] == ["Atrium Menu", "Indian Food"]
    assert len(foods) == 22


def test_public_food_list_only_shows_available_items(client, session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    food = FoodService(session).list_foods()[0]
    food.is_available = False
    session.commit()

    response = client.get("/api/v1/foods")

    assert response.status_code == 200
    returned_names = [item["name"] for item in response.json()]
    assert food.name not in returned_names


def test_admin_can_soft_delete_food(client, session) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    admin_token = seed_admin(session)
    food = FoodService(session).list_foods()[0]

    response = client.delete(
        f"/api/v1/foods/{food.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204
    session.refresh(food)
    assert food.deleted_at is not None
    assert food.is_available is False


def test_admin_can_upload_food_image(client, session, monkeypatch) -> None:
    seed_roles(session)
    CategoryService(session).seed_default_categories()
    FoodService(session).seed_default_menu()
    admin_token = seed_admin(session)
    food = FoodService(session).list_foods()[0]

    uploaded = {}

    def fake_upload(self, *, food_id: str, filename: str, content_type: str | None, content: bytes):
        uploaded["food_id"] = food_id
        uploaded["filename"] = filename
        uploaded["content_type"] = content_type
        uploaded["content"] = content
        return StoredImage(path=f"foods/{food_id}/mock.png", public_url=f"https://example.supabase.co/{food_id}/mock.png")

    def fake_delete(self, path: str) -> None:
        uploaded["deleted_path"] = path

    monkeypatch.setattr("app.infrastructure.supabase_storage.SupabaseStorageService.upload_food_image", fake_upload)
    monkeypatch.setattr("app.infrastructure.supabase_storage.SupabaseStorageService.delete_image", fake_delete)

    response = client.post(
        f"/api/v1/foods/{food.id}/image",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"image": ("test.png", BytesIO(b"fake-image-bytes"), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["image_path"] == f"foods/{food.id}/mock.png"
    assert response.json()["image_url"] == f"https://example.supabase.co/{food.id}/mock.png"
    assert uploaded["filename"] == "test.png"
