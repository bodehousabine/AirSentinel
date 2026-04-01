from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from api.core.config import settings

# Engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
