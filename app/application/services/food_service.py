from decimal import Decimal

from slugify import slugify
from sqlalchemy.orm import Session

from app.infrastructure.database.models.food import FoodItemModel
from app.infrastructure.database.repositories.food_repository import FoodRepository
from app.schemas.food import FoodCreateRequest, FoodUpdateRequest


class FoodService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.foods = FoodRepository(session)

    def list_foods(self):
        return self.foods.list_available()

    def get_food(self, food_id):
        return self.foods.get(food_id)

    def create_food(self, payload: FoodCreateRequest):
        food = FoodItemModel(
            category_id=payload.category_id,
            name=payload.name,
            slug=slugify(payload.name),
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
        if "name" in updates:
            updates["slug"] = slugify(updates["name"])
        for field, value in updates.items():
            setattr(food, field, value)
        self.session.commit()
        self.session.refresh(food)
        return food
