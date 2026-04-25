from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from core.dependencies.auth import get_current_user
from core.models.user import User
from core.schemas.user import UserResponse, UserCreate, UserUpdate
from core.cruds import user as user_crud
from core.settings.database import database_helper
from core.dependencies import require_admin


router = APIRouter(prefix="/users", tags=["Users"])



#=============== Module: Create(view) - Start ===============#
# реализовано в auth
#=============== Module: Create(view) - End ===============#



#=============== Module: Get(view) - Start ===============#
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(database_helper.get_session),
):
    user = await user_crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user

@router.get("/by_username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(database_helper.get_session),
):
    user = await user_crud.get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с именем {username} не найден"
        )
    return user

@router.get("/by_email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: EmailStr,
    session: AsyncSession = Depends(database_helper.get_session)
):
    user = await user_crud.get_user_by_email(session, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с почтой {email} не найден"
        )
    return user
@router.get("/", response_model=list[UserResponse])
async def get_users_admin(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(database_helper.get_session),
):
    return await user_crud.get_users(session, skip, limit)
#=============== Module: Get(view) - End ===============#



#=============== Module: Update(view) - Start ===============#
@router.patch("/update/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        session: AsyncSession = Depends(database_helper.get_session),
):
    user = await user_crud.update_user(session, user_data, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} not found")
    return user
#=============== Module: Update(view) - End ===============#



#=============== Module: Delete(view) - Start ===============#
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(database_helper.get_session),
):
    deleted_user = await user_crud.delete_user(session, user_id)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} not found")
#=============== Module: Delete(view) - End ===============#
