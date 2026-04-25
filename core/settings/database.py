"""
Help with async engine work(create and etc)
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.settings.config import settings


class DataBaseHelper():
    def __init__(self, url: str, echo: bool):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False
        )

    async def get_session(self):
        """Зависимость для получения асинхронной сессии"""
        async with self.session_factory() as session:
            yield session

    async def create_tables(self, base):
        """Создание всех таблиц в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
            
    async def dispose(self):
        """Закрытие движка"""
        await self.engine.dispose()
    


database_helper = DataBaseHelper(
    url=settings.db_url,
    echo=settings.db_echo
)   