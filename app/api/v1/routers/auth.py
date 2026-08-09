from fastapi import APIRouter, Depends

from app.application.services.auth_service import AuthService
from app.dependencies.services import get_auth_service
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
)

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, service: AuthService = Depends(get_auth_service)):
    return service.signup(payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return service.login(payload)


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    return service.refresh(payload)


@router.post("/logout", response_model=MessageResponse)
def logout(payload: LogoutRequest, service: AuthService = Depends(get_auth_service)):
    return service.logout(payload)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)):
    return service.forgot_password(payload)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)):
    return service.reset_password(payload)
