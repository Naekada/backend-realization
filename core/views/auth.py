from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from datetime import datetime, timezone


from core.cruds.user import get_user_by_username, authenticate_user, create_user
from core.models.user import User
from core.schemas import Token, UserCreate, UserResponse, TokenRefreshRequest
from core.utils import create_access_token, create_refresh_token, decode_refresh_token
from core.settings import database_helper, settings
from core.dependencies import get_current_user, o2auth
from core.cruds import add_to_blacklist

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(database_helper.get_session)
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверное имя пользователя или пароль")
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(database_helper.get_session)
):
    user = await get_user_by_username(session, user_data.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Пользователь с таким именем уже существует")
    return await create_user(session, user_data=user_data)


@router.get("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(o2auth),
    session: AsyncSession = Depends(database_helper.get_session)):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            settings.jwt_algorithm,
            options={"verify_exp": False}
        )
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    except Exception:
        expires_at = datetime.now(timezone.utc)

    await add_to_blacklist(
        token=token,
        expires_at=expires_at,
        user_id=current_user.id,
        session=session
    )
    return {"message": "успешный выход из системы"}



@router.post("/refresh", response_model=Token)
async def refreshToken(
    refresh_token: TokenRefreshRequest,
    session: AsyncSession = Depends(database_helper.get_session)
):
    payload = decode_refresh_token(refresh_token.refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный или истекший токен")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный токен")
    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Пользователь не найден")

    new_access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }