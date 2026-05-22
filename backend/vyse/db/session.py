"""Async SQLAlchemy session factory + scope helper."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vyse.core.config import get_settings


@lru_cache(maxsize=1)
def _engine():
    return create_async_engine(get_settings().db_url, future=True, echo=False)


@lru_cache(maxsize=1)
def _sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(_engine(), expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    session = _sessionmaker()()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    """Create tables for the dev SQLite path. In prod, use `alembic upgrade head`."""
    from vyse.db.models import Base

    async with _engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
