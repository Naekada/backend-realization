from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Result, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Comment
from core.schemas import CommentCreate, CommentUpdate


#=============== Start Comment Create ===============#
async def create_comment(
        comment_data: CommentCreate, 
        author_id: int, post_id: int, 
        session: AsyncSession
) -> Comment:
    if not comment_data.content or not comment_data.content.strip():
        raise ValueError("Комментарий не может быть пустым")
    stmt = select(func.max(Comment.comment_number)).where(Comment.post_id == post_id)
    result: Result = await session.execute(stmt)
    max_number = result.scalar() or 0
    new_comment = Comment(
        content=comment_data.content,
        author_id=author_id,
        post_id=post_id,
        comment_number=max_number+1
    )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment
#=============== End Comment Create ===============#


#=============== Start Comment Read ===============#
async def get_comment_by_id(
        comment_id: int, 
        session: AsyncSession
) -> Comment | None:
    stmt = select(Comment).where(Comment.id == comment_id)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_comments_by_author_id(
        author_id: int, 
        session: AsyncSession,
        cursor: int,
        limit: int,
        sort: str = "created_at",
        order: str = "desc"
):
    stmt = select(Comment).where(Comment.author_id == author_id)
    if cursor:
        if order == "desc":
            stmt = stmt.where(Comment.id < cursor)
        else:
            stmt = stmt.where(Comment.id > cursor)

    if sort == "created_at":
        if order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())
        else:
            stmt = stmt.order_by(Comment.created_at.asc())
    stmt = stmt.limit(limit + 1)
    
    result = await session.execute(stmt)
    comments = result.scalars().all()

    next_cursor = None
    if len(cursor) > limit:
        comments = comments[:-1]
        next_cursor = comments[-1].id
    return comments, next_cursor


async def get_comments_by_post_id(
        post_id: int, 
        session: AsyncSession,
        cursor: int,
        limit: int,
        sort: str = "created_at",
        order: str = "desc"
):
    stmt = select(Comment).where(Comment.post_id == post_id)

    if cursor:
        if order == "desc":
            stmt = stmt.where(Comment.id < cursor)
        else:
            stmt = stmt.where(Comment.id > cursor)

    if sort == "created_at":
        if order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())
        else:
            stmt = stmt.order_by(Comment.created_at.asc())

    stmt = stmt.limit(limit + 1)

    result = await session.execute(stmt)
    comments = list(result.scalars().all())
    
    next_cursor = None
    if len(comments) > limit:
        comments = comments[:-1]
        next_cursor = comments[-1].id

    return comments, next_cursor

async def get_comments_in_post_by_author_id(
        author_id: int,
        post_id: int,
        session: AsyncSession
):
    stmt = select(Comment).where(
        Comment.post_id == post_id,
        Comment.author_id == author_id).order_by(Comment.created_at)
    result: Result = await session.execute(stmt)
    return result.scalars().all()

async def get_comments_count_by_post(
        post_id: int,
        session: AsyncSession
) -> int:
    stmt = select(func.count(Comment.id)).where(Comment.post_id == post_id)
    result: Result = await session.execute(stmt)
    return result.scalar()
#=============== End Comment Read ===============#


#=============== Start Comment Update ===============#
async def update_comment_by_id(
        comment_data: CommentUpdate, 
        comment_id: int,
        session: AsyncSession
) ->  Optional[Comment]:
    current_comment = await get_comment_by_id(comment_id, session)
    if not current_comment:
        return None
    update_data = comment_data.model_dump(exclude_unset=True)
    if "content" in update_data and update_data["content"] != current_comment.content:
        update_data["is_edited"] = True
        update_data["edited_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(current_comment, field, value)

    await session.commit()
    await session.refresh(current_comment)
    return current_comment
#=============== End Comment Update ===============#


#=============== Start Comment Delete ===============#
async def delete_comment_by_id(
        comment_id: int,
        session: AsyncSession
) -> bool:
    current_comment = await get_comment_by_id(comment_id, session)
    if not current_comment:
        return False
    await session.delete(current_comment)
    await session.commit()
    return True
#=============== End Comment Delete ===============#