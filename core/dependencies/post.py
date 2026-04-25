from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession 

from core.settings import database_helper
from core.cruds import post as post_crud


async def get_post_or_404(
        post_id: int,
        session: AsyncSession = Depends(database_helper.get_session)
):
    current_post = await post_crud.get_post_by_id(post_id, session)
    if not current_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )
    return current_post
