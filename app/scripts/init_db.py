from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.category_service import CategoryService
from app.application.services.food_service import FoodService
from app.domain.enums import RoleName
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import RoleModel  # noqa: F401
from app.infrastructure.database.session import SessionLocal, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_roles(session: Session) -> None:
    existing = {
        role.name
        for role in session.query(RoleModel).all()
    }
    for role_name in RoleName:
        if role_name.value not in existing:
            session.add(RoleModel(name=role_name.value, description=f"{role_name.value.title()} role"))
    session.commit()


def main() -> None:
    create_tables()
    with SessionLocal() as session:
        seed_roles(session)
        CategoryService(session).seed_default_categories()
        FoodService(session).seed_default_menu()
        AuthService(session).seed_initial_admin()
    print("Database tables created, roles/categories/menu seeded, and optional initial admin provisioned.")


if __name__ == "__main__":
    main()
