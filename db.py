from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

# Use environment variable for database URL with fallback
DB_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:amir@db:5432/mybot"
)

# Ensure we're using asyncpg explicitly
if not DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Import Base from models to avoid duplication
from models import Base

