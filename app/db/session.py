import uuid
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import settings

# Database Engine Configuration
# Supports PostgreSQL with RLS in production, and SQLite for local development/testing
DATABASE_URL = settings.DATABASE_URL
if "sqlite" in DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.LOG_LEVEL.upper() == "DEBUG"
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.LOG_LEVEL.upper() == "DEBUG",
        future=True
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Standard database session dependency.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_tenant_session(tenant_id: uuid.UUID) -> AsyncGenerator[AsyncSession, None]:
    """
    Tenant-Scoped Database Session Context Manager.
    Sets PostgreSQL session configuration variable 'app.current_tenant_id'
    so that Row-Level Security (RLS) policies are actively enforced.
    """
    async with AsyncSessionLocal() as session:
        try:
            bind = session.bind or session.get_bind()
            if bind and bind.dialect.name == "postgresql":
                await session.execute(
                    text("SET LOCAL app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(tenant_id)}
                )
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def set_tenant_context(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """
    Helper to set RLS tenant context on an existing session.
    In PostgreSQL, executes 'SET LOCAL app.current_tenant_id = :tenant_id'.
    """
    bind = session.bind or session.get_bind()
    if bind and bind.dialect.name == "postgresql":
        await session.execute(
            text("SET LOCAL app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
