from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_current_user, get_post_or_404, require_admin_or_author
from core.models.user import User
from core.models.post import Post
from core.schemas import CommentResponse, CommentCreate, CommentUpdate
from core.settings import database_helper
from core.cruds import comment as comment_crud
from core.cruds import post as post_crud 
from core.cruds import user as user_crud


router = APIRouter(prefix="/comments", tags=["Comments"])




#=============== Module: Create(view) - Start ===============#
@router.post("/{post_id}/comments", summary="Создание комментария")
async def create_comment(
    comment_data: CommentCreate,
    post_id: int,
    post: Post = Depends(get_post_or_404),
    author: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    return await comment_crud.create_comment(comment_data, author.id, post_id, session)
#=============== Module: Create(view) - End ===============#


#=============== Module: Get(view) - Start ===============#
@router.get("/user/{user_id}",  summary="Получение комментариев пользователя")
async def get_comments_by_user(
    user_id: int,
    cursor: int,
    limit: int = 10,
    sort: str = "created_at",
    order: str = "desc",
    session: AsyncSession = Depends(database_helper.get_session)
):
    comments, next_cursor = await comment_crud.get_comments_by_author_id(user_id, session, cursor, limit, sort, order)
    if limit > 30: 
        limit = 30
    from fastapi import Response
    response = Response()   
    if next_cursor:
        response.headers["X-Next-Cursor"] = str(next_cursor)
    if not comments:
        return []
    return comments


@router.get("/post/{post_id}/comments", summary="Получение комментариев поста")
async def get_comments_by_post(
    post_id: int,
    cursor: int | None = None,
    limit: int = 10,
    sort: str = "created_at",
    order: str = "desc",
    session: AsyncSession = Depends(database_helper.get_session)
): # с пагинацией
    
    if limit > 30:
        limit = 30

    comments, next_cursor = await comment_crud.get_comments_by_post_id(post_id, session, cursor, limit, sort, order)
    from fastapi import Response
    response = Response()
    if next_cursor:
        response.headers["X-Next-Cursor"] = str(next_cursor)

    return comments

@router.get("/{comment_id}", summary="Получение комментария по ID")
async def get_comment(
    comment_id: int,
    session: AsyncSession = Depends(database_helper.get_session)
):
    comment = await comment_crud.get_comment_by_id(comment_id, session)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    return comment
#=============== Module: Get(view) - End ===============#


#=============== Module: Update(view) - Start ===============#
@router.patch("/update/{comment_id}")
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    current_comment = await comment_crud.get_comment_by_id(comment_id, session)
    if not current_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    await require_admin_or_author(
        comment_author_id=current_comment.author_id, 
        user=current_user
        )

    updated_comment = await comment_crud.update_comment_by_id(comment_data, comment_id, session)
    return updated_comment
#=============== Module: Update(view) - End ===============#


#=============== Module: Delete(view) - Start ===============#
@router.delete("/")
async def delete_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    comment = await comment_crud.get_comment_by_id(comment_id, session)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    await require_admin_or_author(user=user, comment_author_id=comment.author_id)
    await comment_crud.delete_comment_by_id(comment_id, session)
#=============== Module: Delete(view) - End ===============#
