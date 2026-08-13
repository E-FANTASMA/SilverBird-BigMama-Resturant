import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.domain.enums import RoleName

PASSWORD_STRENGTH_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")
PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


class PhonePasswordValidationMixin(BaseModel):
    @field_validator("phone", mode="before", check_fields=False)
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = re.sub(r"[\s\-()]", "", value)
        if normalized.startswith("0") and len(normalized) == 11 and normalized.isdigit():
            normalized = f"+234{normalized[1:]}"
        if normalized and not PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("Phone number must be in a valid international format")
        return normalized

    @field_validator("password", mode="after", check_fields=False)
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not PASSWORD_STRENGTH_PATTERN.fullmatch(value):
            raise ValueError(
                "Password must be at least 8 characters and include uppercase, lowercase, number, and symbol"
            )
        return value


class SignupRequest(PhonePasswordValidationMixin):
    role: RoleName = RoleName.CUSTOMER
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)

    @field_validator("role")
    @classmethod
    def validate_signup_role(cls, value: RoleName) -> RoleName:
        if value not in {RoleName.CUSTOMER, RoleName.DELIVERY_PERSONNEL}:
            raise ValueError("Only customer and delivery accounts can sign up here")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(PhonePasswordValidationMixin):
    reset_token: str
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class PrivilegedUserCreateRequest(PhonePasswordValidationMixin):
    role: RoleName
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: RoleName) -> RoleName:
        if value not in {RoleName.ADMIN, RoleName.DELIVERY_PERSONNEL}:
            raise ValueError("Only admin and delivery personnel accounts can be provisioned here")
        return value


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str


class ForgotPasswordResponse(MessageResponse):
    reset_token: str | None = None
