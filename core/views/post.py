from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_admin_or_author
from core.models.user import User
from core.schemas.post import PostResponse, PostCreate, PostUpdate
from core.settings import database_helper
from core.cruds import post as post_crud


router = APIRouter(prefix="/posts", tags=["Posts"])


#=============== Module: Create(view) - Start ===============#
@router.post("/create", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    author: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    return await post_crud.create_post(post_data, session, author.id)
#=============== Module: Create(view) - End ===============#


#=============== Module: Get(view) - Start ===============#
@router.get("/me", response_model=list[PostResponse])
async def get_my_posts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    posts = await post_crud.get_posts_by_author(current_user.id, session)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"У пользователя {current_user.username} не найдено постов")
    return posts


@router.get("/post/{post_id}", response_model=PostResponse)
async def get_post_by_id_view(
    post_id: int,
    session: AsyncSession = Depends(database_helper.get_session)
):
    post = await post_crud.get_post_by_id(post_id, session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Пост с ID: {post_id} не найден")
    return post

@router.get("/author/{author_id}", response_model=list[PostResponse])
async def get_posts_by_author_view(
    author_id: int,
    session: AsyncSession = Depends(database_helper.get_session)
):
    posts = await post_crud.get_posts_by_author(author_id, session)
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользовталеь с ID: {author_id} не найден"
        )
    return posts

@router.get("/cursor", response_model=list[PostResponse])
async def get_posts_cursor(
    cursor: int | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(database_helper.get_session)
):
    posts, next_cursor = await post_crud.get_posts_cursor(session, cursor, limit)

    from fastapi import Response
    response = Response()
    if next_cursor:
        response.headers["X-Next-Cursor"] = str(next_cursor)
    return posts
#=============== Module: Get(view) - End ===============#


#=============== Module: Update(view) - Start ===============#
@router.patch("/update/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    author: User = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.get_session)
):
    post = await post_crud.update_post(post_data=post_data, post_id=post_id, session=session)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пост с ID: {post_id} не найден"
        )
    await require_admin_or_author(user=author, post_author_id=post.author_id)
    return post
#=============== Module: Update(view) - End ===============#



#=============== Module: Delete(view) - Start ===============#
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_by_id(
    post_id: int,
    session: AsyncSession = Depends(database_helper.get_session),
    author: User = Depends(get_current_user)
):
    post = await post_crud.get_post_by_id(post_id, session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Пост с id: {post_id} не найден")
    await require_admin_or_author(user=author, post_author_id=post.author_id)
    await post_crud.delete_post(session, post_id)
#=============== Module: Delete(view) - End ===============#



