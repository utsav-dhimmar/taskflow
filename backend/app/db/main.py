from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import setting

# sync driver -> make it async driver
# If DB is sqlite then url start with  sqlite://... -> sqlite+aiosqlite:///...
# If DB is postgresql then url start with  postgresql://... -> postgresql+asyncpg://...
# postgresql://user:password@hostname:port/database_name

database_url = setting.DATABASE_URL
if database_url and database_url.startswith("postgresql://"):
    if "postgresql+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")


connect_args = {"check_same_thread": False}
print(database_url)
engine = create_async_engine(database_url, echo=True)
# engine = create_async_engine(database_url, echo=True, connect_args=connect_args)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # await conn.execute(text("PRAGMA journal_mode=WAL;"))
        await conn.run_sync(SQLModel.metadata.create_all)
