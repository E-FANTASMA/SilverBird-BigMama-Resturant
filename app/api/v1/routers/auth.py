from fastapi import APIRouter, Depends

from app.application.services.auth_service import AuthService
from app.dependencies.services import get_auth_service
from app.schemas.auth import AuthResponse, LoginRequest, RefreshTokenRequest, SignupRequest

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


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logout endpoint reserved for refresh-token revocation flow."}
