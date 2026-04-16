from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AuthTokens, LoginRequest, RefreshRequest, UserProfile
from app.services import repository
from app.services.security import create_access_token, create_refresh_token, decode_token

router = APIRouter()


@router.post("/login", response_model=AuthTokens)
def login(payload: LoginRequest, session: Session = Depends(get_db_session)) -> AuthTokens:
    user = repository.authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return AuthTokens(
        accessToken=create_access_token(user.id, user.role),
        refreshToken=create_refresh_token(user.id),
        tokenType="bearer",
        expiresIn=7200,
    )


@router.post("/refresh", response_model=AuthTokens)
def refresh(payload: RefreshRequest, session: Session = Depends(get_db_session)) -> AuthTokens:
    try:
        token_payload = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = str(token_payload.get("sub", ""))
    user = repository.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return AuthTokens(
        accessToken=create_access_token(user.id, user.role),
        refreshToken=create_refresh_token(user.id),
        tokenType="bearer",
        expiresIn=7200,
    )


@router.get("/me", response_model=UserProfile)
def me(user: User = Depends(get_current_user)) -> UserProfile:
    return UserProfile(id=user.id, name=user.name, email=user.email, role=user.role)
