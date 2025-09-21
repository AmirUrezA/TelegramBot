"""
Pytest Configuration and Fixtures
Enterprise-level testing configuration
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.services.database import DatabaseService
from app.services.user_service import UserService
from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.config.settings import ApplicationConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create test database"""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_service(test_db):
    """Create database service for testing"""
    db = DatabaseService()
    db.engine = test_db
    db.session_maker = async_sessionmaker(test_db, expire_on_commit=False)
    db._initialized = True
    return db


@pytest.fixture
def mock_config():
    """Create mock configuration"""
    class MockConfig:
        class MockTelegram:
            bot_token = "test_token"
            admin_username = "test_admin"
        
        class MockSMS:
            kavenegar_api_key = "test_key"
        
        class MockPayment:
            card_number = "1234567890"
            card_holder_name = "Test Holder"
        
        telegram = MockTelegram()
        sms = MockSMS()
        payment = MockPayment()
    
    return MockConfig()


@pytest.fixture
def mock_sms_service(mock_config):
    """Create mock SMS service"""
    class MockSMSService:
        def generate_otp(self, length=4):
            return "1234"
        
        async def send_otp(self, phone, otp):
            return {"success": True}
    
    return MockSMSService()


@pytest.fixture
def mock_notification_service():
    """Create mock notification service"""
    class MockNotificationService:
        async def send_to_admin(self, message):
            return True
        
        async def send_registration_notification(self, **kwargs):
            return True
        
        async def send_order_notification(self, **kwargs):
            return True
    
    return MockNotificationService()


@pytest.fixture
async def user_service(db_service):
    """Create user service for testing"""
    return UserService()


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "full_name": "تست کاربر",
        "city": "تهران",
        "area": "1",
        "national_id": "1234567890",
        "phone": "09123456789"
    }
