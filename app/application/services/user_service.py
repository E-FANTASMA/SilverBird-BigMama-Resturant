from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.schemas.user import ProfileUpdateRequest


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def get_profile(self, user_id):
        user = self.session.get(self.users.model_type, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def update_profile(self, user_id, payload: ProfileUpdateRequest):
        user = self.get_profile(user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.session.commit()
        self.session.refresh(user)
        return user
