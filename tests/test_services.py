"""
Service Layer Tests
Unit tests for business logic services
"""

import pytest
from app.services.user_service import UserService
from app.exceptions.base import ValidationException, UserNotFoundException


@pytest.mark.asyncio
async def test_user_service_create_user(user_service, sample_user_data):
    """Test user creation"""
    user = await user_service.complete_registration(**sample_user_data)
    
    assert user.telegram_id == sample_user_data["telegram_id"]
    assert user.username == sample_user_data["username"]
    assert user.approved is True


@pytest.mark.asyncio
async def test_user_service_validation_invalid_name(user_service, sample_user_data):
    """Test user creation with invalid name"""
    sample_user_data["full_name"] = "Invalid123"
    
    with pytest.raises(ValidationException):
        await user_service.complete_registration(**sample_user_data)


@pytest.mark.asyncio
async def test_user_service_validation_invalid_phone(user_service, sample_user_data):
    """Test user creation with invalid phone"""
    sample_user_data["phone"] = "invalid_phone"
    
    with pytest.raises(ValidationException):
        await user_service.complete_registration(**sample_user_data)


@pytest.mark.asyncio
async def test_user_service_get_nonexistent_user(user_service):
    """Test getting non-existent user"""
    user = await user_service.get_user_by_telegram_id(999999)
    assert user is None


@pytest.mark.asyncio
async def test_user_service_require_registered_user_not_found(user_service):
    """Test requiring registered user that doesn't exist"""
    with pytest.raises(UserNotFoundException):
        await user_service.require_registered_user(999999)


@pytest.mark.asyncio 
async def test_sms_service_generate_otp(mock_sms_service):
    """Test OTP generation"""
    otp = mock_sms_service.generate_otp()
    assert len(otp) == 4
    assert otp.isdigit()


@pytest.mark.asyncio
async def test_sms_service_send_otp(mock_sms_service):
    """Test OTP sending"""
    result = await mock_sms_service.send_otp("09123456789", "1234")
    assert result["success"] is True
