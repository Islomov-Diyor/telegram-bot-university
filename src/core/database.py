from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

# SQLite optimization: connect_args={"check_same_thread": False}
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database session to FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database if they don't exist and run non-destructive schema migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def run_lightweight_migrations(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)

            # 1. clubs table: registration_deadline
            if "clubs" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("clubs")]
                if "registration_deadline" not in columns:
                    sync_conn.execute(text("ALTER TABLE clubs ADD COLUMN registration_deadline DATETIME NULL"))

            # 2. registrations table: queue_position
            if "registrations" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("registrations")]
                if "queue_position" not in columns:
                    sync_conn.execute(text("ALTER TABLE registrations ADD COLUMN queue_position INTEGER NULL"))

            # 3. students table: language
            if "students" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("students")]
                if "language" not in columns:
                    sync_conn.execute(text("ALTER TABLE students ADD COLUMN language VARCHAR(10) DEFAULT 'uz'"))

        await conn.run_sync(run_lightweight_migrations)

