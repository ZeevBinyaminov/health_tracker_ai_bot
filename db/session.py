from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DATABASE_URL
from db.base import Base

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker[AsyncSession](
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully")
