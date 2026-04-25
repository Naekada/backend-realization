from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from core.schemas.user import UserCreate, UserUpdate
from core.models import User
from core.utils import verify_password, hash_password


#===============Start Create Users===============#
async def create_user(
        session: AsyncSession, 
        user_data: UserCreate) -> User:
    newUser = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    session.add(newUser)
    await session.commit()
    await session.refresh(newUser)
    return newUser
#===============End Create Users===============#


#===============Start Read Users===============#
async def get_user_by_id(
        session: AsyncSession,
        user_id: int
) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
    
async def get_user_by_username(
        session: AsyncSession,
        username: str
) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(
        session: AsyncSession,
        email: EmailStr
) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_users(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
) -> list[User]:
    result = await session.execute(select(User)
                                   .offset(skip)
                                   .limit(limit)
                                   .order_by(User.id))
    return list(result.scalars().all())
#===============End Read Users===============#


#===============Start Update Users===============#
async def update_user(
        session: AsyncSession,
        user_data: UserUpdate,
        user_id: int
) -> User:
    currentUser = await get_user_by_id(session=session, user_id=user_id)
    if not currentUser:
        return None
    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(currentUser, field, value)
    await session.commit()
    await session.refresh(currentUser) 
    return currentUser
#===============End Update Users===============#


#===============Start Delete Users===============#
async def delete_user(
        session: AsyncSession,
        user_id: int
) -> bool:
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True
#===============End Delete Users===============#


#===============Start Authenticate Users===============#
async def authenticate_user(
        username: str,
        password: str,
        session: AsyncSession
):
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user 
#===============End Authenticate Users===============#
