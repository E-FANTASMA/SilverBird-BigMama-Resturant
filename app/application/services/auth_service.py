from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.domain.enums import RoleName
from app.infrastructure.database.models.cart import CartModel
from app.infrastructure.database.models.token import RefreshTokenModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.repositories.role_repository import RoleRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, LoginRequest, RefreshTokenRequest, SignupRequest


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)

    def signup(self, payload: SignupRequest) -> AuthResponse:
        if self.users.get_by_email(payload.email):
            raise ConflictException("Email already exists")

        customer_role = self.roles.get_by_name(RoleName.CUSTOMER)
        if not customer_role:
            raise ConflictException("Customer role is not seeded")

        user = UserModel(
            role_id=customer_role.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
        )
        self.session.add(user)
        self.session.flush()
        self.session.add(CartModel(user_id=user.id))
        tokens = self._issue_tokens(user)
        self.session.commit()
        return tokens

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        user.last_login_at = datetime.now(UTC)
        tokens = self._issue_tokens(user)
        self.session.commit()
        return tokens

    def refresh(self, payload: RefreshTokenRequest) -> AuthResponse:
        # In a production implementation we would validate and rotate persisted refresh tokens.
        return AuthResponse(
            access_token=create_access_token(payload.user_id),
            refresh_token=create_refresh_token(payload.user_id),
            token_type="bearer",
        )

    def _issue_tokens(self, user: UserModel) -> AuthResponse:
        access_token = create_access_token(user.id, {"role": user.role.name if user.role else None})
        refresh_token = create_refresh_token(user.id)
        refresh_record = RefreshTokenModel(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        self.session.add(refresh_record)
        return AuthResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
