from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from core.settings import database_helper
from core.utils import decode_access_token
from core.cruds import user as user_crud
from core.cruds import is_blacklisted


o2auth = OAuth2PasswordBearer(tokenUrl="/auth/login")



async def get_current_user(
        token: str = Depends(o2auth),
        session: AsyncSession = Depends(database_helper.get_session)
) -> User | None:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный или просроченный токен", 
            headers={"WWW-Authenticate": "Bearer"})
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный токен")
    user = await user_crud.get_user_by_username(session, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Пользователь не найден")
    if await is_blacklisted(session, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван")
    return user
