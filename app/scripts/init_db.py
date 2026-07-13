from __future__ import annotations

from sqlalchemy.orm import Session

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
    print("Database tables created and roles seeded.")


if __name__ == "__main__":
    main()
