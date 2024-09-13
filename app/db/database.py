from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.declarative import DeclarativeMeta

from dotenv import load_dotenv
from os import getenv

from typing import AsyncGenerator

load_dotenv()
DATABASE_URL: str = getenv("DB_URL")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
metadata: MetaData = MetaData()
Base: DeclarativeMeta = declarative_base()

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        await init_db()
        yield session
