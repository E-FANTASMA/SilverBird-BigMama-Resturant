import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException, ValidationException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.domain.enums import RoleName
from app.infrastructure.database.models.cart import CartModel
from app.infrastructure.database.models.token import PasswordResetTokenModel, RefreshTokenModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.repositories.role_repository import RoleRepository
from app.infrastructure.database.repositories.token_repository import (
    PasswordResetTokenRepository,
    RefreshTokenRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    PrivilegedUserCreateRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
)


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.password_reset_tokens = PasswordResetTokenRepository(session)

    def signup(self, payload: SignupRequest) -> AuthResponse:
        customer_role = self._get_role(RoleName.CUSTOMER)
        user = self._create_user(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            phone=payload.phone,
            password=payload.password,
            is_verified=False,
            role_id=customer_role.id,
        )
        self.session.add(CartModel(user_id=user.id))
        tokens = self._issue_tokens(user, customer_role.name)
        self.session.commit()
        return tokens

    def create_privileged_user(self, payload: PrivilegedUserCreateRequest) -> UserModel:
        role = self._get_role(payload.role)
        user = self._create_user(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            phone=payload.phone,
            password=payload.password,
            is_verified=True,
            role_id=role.id,
        )
        self.session.commit()
        self.session.refresh(user)
        return user

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active or user.deleted_at is not None:
            raise UnauthorizedException("This account is inactive")
        user.last_login_at = datetime.now(UTC)
        tokens = self._issue_tokens(user, user.role.name)
        self.session.commit()
        return tokens

    def refresh(self, payload: RefreshTokenRequest) -> AuthResponse:
        token_payload = self._decode_refresh_payload(payload.refresh_token)
        user = self._get_user_from_token_subject(token_payload["user_id"])
        self._validate_user_for_auth(user)
        stored_token = self._find_matching_refresh_token(user.id, payload.refresh_token)
        if stored_token.revoked_at is not None or self._is_expired(stored_token.expires_at):
            raise UnauthorizedException("Refresh token is no longer valid")
        self.refresh_tokens.revoke(stored_token)
        tokens = self._issue_tokens(user, user.role.name)
        self.session.commit()
        return tokens

    def logout(self, payload: LogoutRequest) -> MessageResponse:
        token_payload = self._decode_refresh_payload(payload.refresh_token)
        stored_token = self._find_matching_refresh_token(token_payload["user_id"], payload.refresh_token)
        if stored_token.revoked_at is None:
            self.refresh_tokens.revoke(stored_token)
            self.session.commit()
        return MessageResponse(message="Logout successful")

    def forgot_password(self, payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
        message = "If an account with that email exists, a password reset link has been initiated"
        user = self.users.get_by_email(str(payload.email))
        if not user or not user.is_active or user.deleted_at is not None:
            return ForgotPasswordResponse(message=message)

        for token in self.password_reset_tokens.list_active_by_user_id(user.id):
            token.used_at = datetime.now(UTC)

        raw_token = secrets.token_urlsafe(48)
        self.session.add(
            PasswordResetTokenModel(
                user_id=user.id,
                token_hash=hash_password(raw_token),
                expires_at=datetime.now(UTC) + timedelta(minutes=self.settings.password_reset_token_expire_minutes),
            )
        )
        self.session.commit()
        response = ForgotPasswordResponse(message=message)
        if self.settings.debug or self.settings.environment.lower() != "production":
            response.reset_token = raw_token
        return response

    def reset_password(self, payload: ResetPasswordRequest) -> MessageResponse:
        raw_token = payload.reset_token.strip()
        matched_token: PasswordResetTokenModel | None = None
        for reset_token in self.password_reset_tokens.list_active():
            if verify_password(raw_token, reset_token.token_hash):
                matched_token = reset_token
                break

        if not matched_token:
            raise UnauthorizedException("Invalid or expired reset token")
        matched_user = self._get_user_from_token_subject(matched_token.user_id)
        if self._is_expired(matched_token.expires_at):
            raise UnauthorizedException("Invalid or expired reset token")
        self._validate_user_for_auth(matched_user)

        matched_user.password_hash = hash_password(payload.password)
        matched_token.used_at = datetime.now(UTC)
        self.refresh_tokens.revoke_all_for_user(matched_user.id)
        self.session.commit()
        return MessageResponse(message="Password reset successful")

    def seed_initial_admin(self) -> UserModel | None:
        if not self.settings.initial_admin_email or not self.settings.initial_admin_password:
            return None
        existing_user = self.users.get_by_email(self.settings.initial_admin_email)
        if existing_user:
            return existing_user
        role = self._get_role(RoleName.ADMIN)
        user = self._create_user(
            first_name=self.settings.initial_admin_first_name or "System",
            last_name=self.settings.initial_admin_last_name or "Admin",
            email=self.settings.initial_admin_email,
            phone=self.settings.initial_admin_phone,
            password=self.settings.initial_admin_password,
            is_verified=True,
            role_id=role.id,
        )
        self.session.commit()
        self.session.refresh(user)
        return user

    def _create_user(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None,
        password: str,
        is_verified: bool,
        role_id,
    ) -> UserModel:
        self._ensure_unique_identity(email, phone)
        user = UserModel(
            role_id=role_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.lower(),
            phone=phone,
            password_hash=hash_password(password),
            is_verified=is_verified,
        )
        self.session.add(user)
        self.session.flush()
        return user

    def _ensure_unique_identity(self, email: str, phone: str | None) -> None:
        if self.users.get_by_email(email):
            raise ConflictException("Email already exists")
        if phone and self.users.get_by_phone(phone):
            raise ConflictException("Phone number already exists")

    def _issue_tokens(self, user: UserModel, role_name: str) -> AuthResponse:
        access_token = create_access_token(user.id, {"role": role_name})
        refresh_token = create_refresh_token(user.id, {"role": role_name})
        refresh_record = RefreshTokenModel(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days),
        )
        self.session.add(refresh_record)
        return AuthResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    def _decode_refresh_payload(self, refresh_token: str) -> dict[str, UUID]:
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise UnauthorizedException(str(exc)) from exc
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
        return {"user_id": UUID(str(user_id))}

    def _find_matching_refresh_token(self, user_id, raw_token: str) -> RefreshTokenModel:
        for stored_token in self.refresh_tokens.list_active_by_user_id(user_id):
            if verify_password(raw_token, stored_token.token_hash):
                return stored_token
        raise UnauthorizedException("Refresh token is no longer valid")

    def _validate_user_for_auth(self, user: UserModel) -> None:
        if not user.is_active or user.deleted_at is not None:
            raise UnauthorizedException("This account is inactive")

    def _get_role(self, role_name: RoleName):
        role = self.roles.get_by_name(role_name)
        if not role:
            raise ValidationException(f"{role_name.value.title()} role is not seeded")
        return role

    def _get_user_from_token_subject(self, user_id: UUID) -> UserModel:
        try:
            return self.users.get(user_id)
        except NotFoundException as exc:
            raise UnauthorizedException("User for this token was not found") from exc

    def _is_expired(self, value: datetime) -> bool:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value <= datetime.now(UTC)
