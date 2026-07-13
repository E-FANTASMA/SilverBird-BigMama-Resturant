from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException

ModelType = TypeVar("ModelType")


class SQLAlchemyRepository(Generic[ModelType]):
    def __init__(self, session: Session, model_type: type[ModelType]) -> None:
        self.session = session
        self.model_type = model_type

    def get(self, record_id):
        record = self.session.get(self.model_type, record_id)
        if not record:
            raise NotFoundException(f"{self.model_type.__name__} not found")
        return record

    def list(self):
        return self.session.scalars(select(self.model_type)).all()

    def add(self, model: ModelType) -> ModelType:
        self.session.add(model)
        return model

    def delete(self, model: ModelType) -> None:
        self.session.delete(model)
