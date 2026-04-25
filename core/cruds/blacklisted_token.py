from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select
from datetime import datetime
from core.models import BlacklistedToken

async def add_to_blacklist(token: str, expires_at: datetime, user_id: int, session: AsyncSession):
    nonactive_token = BlacklistedToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    session.add(nonactive_token)
    await session.commit()
    
async def is_blacklisted(session: AsyncSession, token: str): 
    stmt = select(BlacklistedToken).where(BlacklistedToken.token == token)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None

async def cleanup_expired_tokens(session: AsyncSession):
    stmt = select(BlacklistedToken).where(BlacklistedToken.expires_at <= datetime.now())
    result: Result = await session.execute(stmt)
    tokens = result.scalars().all()
    for token in tokens:
        await session.delete(token)
    await session.commit()
    return len(tokens)