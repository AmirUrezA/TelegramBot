"""
Database Service Layer
Enterprise-level database operations and session management
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Type, TypeVar, Generic, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config.settings import config
from app.models.base import Base, BaseModel
from app.exceptions.base import DatabaseException
from app.utils.logging import database_logger

T = TypeVar('T', bound=BaseModel)


class DatabaseService:
    """Enterprise database service with session management"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize database engine and session maker"""
        if self._initialized:
            return
        
        self.engine = create_async_engine(
            config.database.url,
            echo=config.database.echo_queries,
            pool_size=config.database.pool_size,
            max_overflow=config.database.pool_overflow,
            pool_timeout=config.database.pool_timeout,
            pool_pre_ping=True,  # Verify connections before use
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._initialized = True
        database_logger.info("Database service initialized")
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session with proper cleanup"""
        if not self._initialized:
            raise DatabaseException(
                operation="get_session",
                error_details="Database service not initialized"
            )
        
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                database_logger.error(f"Database session error: {str(e)}", exc_info=True)
                raise DatabaseException(
                    operation="session_operation",
                    error_details=str(e)
                )
            finally:
                await session.close()
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        if not self.engine:
            raise DatabaseException(
                operation="create_tables",
                error_details="Database engine not initialized"
            )
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        database_logger.info("Database tables created")
    
    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution)"""
        if not self.engine:
            raise DatabaseException(
                operation="drop_tables",
                error_details="Database engine not initialized"
            )
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        database_logger.warning("Database tables dropped")
    
    async def close(self) -> None:
        """Close database engine"""
        if self.engine:
            await self.engine.dispose()
            database_logger.info("Database engine closed")


class BaseRepository(Generic[T]):
    """Generic repository for database operations"""
    
    def __init__(self, model_class: Type[T], db_service: DatabaseService):
        self.model_class = model_class
        self.db_service = db_service
    
    async def create(self, **kwargs) -> T:
        """Create a new record"""
        async with self.db_service.get_session() as session:
            try:
                instance = self.model_class(**kwargs)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                
                database_logger.debug(f"Created {self.model_class.__name__} with ID {instance.id}")
                return instance
                
            except IntegrityError as e:
                raise DatabaseException(
                    operation="create",
                    error_details=f"Integrity constraint violation: {str(e)}"
                )
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="create",
                    error_details=str(e)
                )
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID"""
        async with self.db_service.get_session() as session:
            try:
                result = await session.get(self.model_class, id)
                return result
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="get_by_id",
                    error_details=str(e)
                )
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Get record by specific field"""
        async with self.db_service.get_session() as session:
            try:
                stmt = select(self.model_class).where(getattr(self.model_class, field_name) == value)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="get_by_field",
                    error_details=str(e)
                )
    
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all records with optional pagination"""
        async with self.db_service.get_session() as session:
            try:
                stmt = select(self.model_class).offset(offset)
                if limit:
                    stmt = stmt.limit(limit)
                
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="get_all",
                    error_details=str(e)
                )
    
    async def update(self, id: int, **kwargs) -> Optional[T]:
        """Update record by ID"""
        async with self.db_service.get_session() as session:
            try:
                stmt = update(self.model_class).where(self.model_class.id == id).values(**kwargs)
                await session.execute(stmt)
                await session.commit()
                
                # Fetch updated record
                result = await session.get(self.model_class, id)
                database_logger.debug(f"Updated {self.model_class.__name__} with ID {id}")
                return result
                
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="update",
                    error_details=str(e)
                )
    
    async def delete(self, id: int) -> bool:
        """Delete record by ID"""
        async with self.db_service.get_session() as session:
            try:
                stmt = delete(self.model_class).where(self.model_class.id == id)
                result = await session.execute(stmt)
                await session.commit()
                
                deleted = result.rowcount > 0
                if deleted:
                    database_logger.debug(f"Deleted {self.model_class.__name__} with ID {id}")
                
                return deleted
                
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="delete",
                    error_details=str(e)
                )
    
    async def count(self) -> int:
        """Get total count of records"""
        async with self.db_service.get_session() as session:
            try:
                stmt = select(func.count(self.model_class.id))
                result = await session.execute(stmt)
                return result.scalar()
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="count",
                    error_details=str(e)
                )
    
    async def exists(self, **filters) -> bool:
        """Check if record exists with given filters"""
        async with self.db_service.get_session() as session:
            try:
                stmt = select(self.model_class)
                for field_name, value in filters.items():
                    stmt = stmt.where(getattr(self.model_class, field_name) == value)
                
                stmt = stmt.limit(1)
                result = await session.execute(stmt)
                return result.first() is not None
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="exists",
                    error_details=str(e)
                )
    
    async def find(self, **filters) -> List[T]:
        """Find records by filters"""
        async with self.db_service.get_session() as session:
            try:
                stmt = select(self.model_class)
                for field_name, value in filters.items():
                    stmt = stmt.where(getattr(self.model_class, field_name) == value)
                
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except SQLAlchemyError as e:
                raise DatabaseException(
                    operation="find",
                    error_details=str(e)
                )


# Global database service instance
db_service = DatabaseService()
