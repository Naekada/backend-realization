from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import PostCreate, PostUpdate
from core.models import Post

#===============Start Create Posts===============#
async def create_post(
        post_data: PostCreate,
        session: AsyncSession,
        author_id: int
):
    newPost = Post(
        title=post_data.title,
        description=post_data.description,
        author_id=author_id
    )
    session.add(newPost)
    await session.commit()
    await session.refresh(newPost)
    return newPost
#===============End Create Posts===============#


#===============Start Read Posts===============#
async def get_post_by_id(
        post_id: int, 
        session: AsyncSession
) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_posts_by_author(
        author_id: int,
        session: AsyncSession
):
    stmt = select(Post).where(Post.author_id == author_id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())

async def get_posts_cursor(
        session: AsyncSession,
        cursor: int | None = None,
        limit: int = 100
):
    stmt = select(Post).order_by(Post.id)
    if cursor:
        stmt = stmt.where(Post.id < cursor)
    stmt = stmt.limit(limit + 1)
    
    result = await session.execute(stmt)
    posts = result.scalars().all()
    
    next_cursor = None
    if len(posts) > limit:
        posts = posts[:-1]
        next_cursor = posts[-1].id if posts else None
    
    return posts, next_cursor
#===============End Read Posts===============#


#===============Start Update Posts===============#
async def update_post(
        post_data: PostUpdate,
        post_id: int,
        session: AsyncSession,
):
    current_post: Post = await get_post_by_id(post_id, session)
    if not current_post:
        return None
    
    for field, value in post_data.model_dump(exclude_unset=True).items():
        setattr(current_post, field, value)

    await session.commit()
    await session.refresh(current_post)
    return current_post
#===============End Update Posts===============#


#===============Start Delete Posts===============#
async def delete_post(
        session: AsyncSession,
        post_id: int
):
    current_post = await get_post_by_id(post_id, session)
    if not current_post:
        return False
    await session.delete(current_post)
    await session.commit()
    return True
#===============End Delete Posts===============#

