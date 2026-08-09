from decimal import Decimal
from datetime import UTC, datetime

from slugify import slugify
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.core.menu_seed_data import DEFAULT_MENU_CATEGORIES
from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.repositories.category_repository import CategoryRepository
from app.infrastructure.database.repositories.food_repository import FoodRepository
from app.infrastructure.supabase_storage import SupabaseStorageService
from app.schemas.food import FoodCreateRequest, FoodUpdateRequest


class FoodService:
    def __init__(self, session: Session, storage: SupabaseStorageService | None = None) -> None:
        self.session = session
        self.foods = FoodRepository(session)
        self.categories = CategoryRepository(session)
        self.storage = storage

    def list_foods(self):
        return self.foods.list_available()

    def get_food(self, food_id):
        food = self.foods.get(food_id)
        if food.deleted_at is not None or not food.is_available:
            raise NotFoundException("Food item not found")
        return food

    def create_food(self, payload: FoodCreateRequest):
        self.categories.get(payload.category_id)
        slug = slugify(payload.name)
        if self.foods.get_active_by_slug(slug):
            raise ConflictException("Food item already exists")
        food = FoodItemModel(
            category_id=payload.category_id,
            name=payload.name,
            slug=slug,
            description=payload.description,
            price=Decimal(str(payload.price)),
            preparation_time_minutes=payload.preparation_time_minutes,
        )
        self.foods.add(food)
        self.session.commit()
        self.session.refresh(food)
        return food

    def update_food(self, food_id, payload: FoodUpdateRequest):
        food = self.foods.get(food_id)
        updates = payload.model_dump(exclude_unset=True)
        if food.deleted_at is not None:
            raise NotFoundException("Food item not found")
        if "category_id" in updates:
            self.categories.get(updates["category_id"])
        if "name" in updates:
            updates["slug"] = slugify(updates["name"])
            existing = self.foods.get_active_by_slug(updates["slug"])
            if existing and existing.id != food.id:
                raise ConflictException("Food item already exists")
        for field, value in updates.items():
            setattr(food, field, value)
        self.session.commit()
        self.session.refresh(food)
        return food

    def delete_food(self, food_id) -> None:
        food = self.foods.get(food_id)
        if food.deleted_at is None:
            self._delete_image_if_present(food)
            food.deleted_at = datetime.now(UTC)
            food.is_available = False
            food.image_path = None
            food.image_url = None
            self.session.commit()

    def seed_default_menu(self) -> None:
        categories_by_slug = {category.slug: category for category in self.categories.list_active()}
        for category_data in DEFAULT_MENU_CATEGORIES:
            category = categories_by_slug.get(slugify(category_data["name"]))
            if not category:
                continue
            for item in category_data["items"]:
                slug = slugify(item["name"])
                if self.foods.get_active_by_slug(slug):
                    continue
                self.foods.add(
                    FoodItemModel(
                        category_id=category.id,
                        name=item["name"],
                        slug=slug,
                        description=item["description"],
                        price=Decimal(item["price"]),
                    )
                )
        self.session.commit()

    def upload_food_image(self, food_id, *, filename: str, content_type: str | None, content: bytes):
        if not self.storage:
            raise NotFoundException("Storage service is not configured")
        food = self.foods.get(food_id)
        if food.deleted_at is not None:
            raise NotFoundException("Food item not found")
        stored_image = self.storage.upload_food_image(
            food_id=str(food.id),
            filename=filename,
            content_type=content_type,
            content=content,
        )
        self._delete_image_if_present(food)
        food.image_path = stored_image.path
        food.image_url = stored_image.public_url
        self.session.commit()
        self.session.refresh(food)
        return food

    def _delete_image_if_present(self, food: FoodItemModel) -> None:
        if self.storage and food.image_path:
            self.storage.delete_image(food.image_path)
