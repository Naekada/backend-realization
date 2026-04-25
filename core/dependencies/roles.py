from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from core.models import User


async def require_admin(
        user: User = Depends(get_current_user)
) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return user


async def require_admin_or_author(
        user: User,
        post_author_id: int | None = None,
        comment_author_id: int | None = None,
) -> bool:
    if user.role == "admin" or user.id == post_author_id or user.id == comment_author_id:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав"
        )
