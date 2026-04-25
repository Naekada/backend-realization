import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from main import app
from core.models import Base
from core.settings.database import database_helper


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.sqlite3"




@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура: создает чистую БД для каждого теста"""
    TestEngine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with TestEngine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    TestAsyncSessionMaker = async_sessionmaker(TestEngine, expire_on_commit=False)
    async with TestAsyncSessionMaker() as session:
        yield session

    await TestEngine.dispose()

@pytest.fixture
async def client(session: AsyncSession):
    """Фикстура: клиент для запросов к API"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        app.dependency_overrides[database_helper.get_session] = lambda: session
        yield client
    app.dependency_overrides.clear()