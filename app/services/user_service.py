"""
User Service Layer
Business logic for user management and registration
"""

from typing import Optional, Tuple
from app.models import User
from app.services.database import BaseRepository, db_service
from app.exceptions.base import UserNotFoundException, UserNotRegisteredException, ValidationException
from app.utils.validation import InputValidator
from app.utils.logging import auth_logger


class UserService:
    """Service for user-related business operations"""
    
    def __init__(self):
        self.repository = BaseRepository(User, db_service)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        try:
            return await self.repository.get_by_field("telegram_id", telegram_id)
        except Exception as e:
            auth_logger.error(f"Error getting user by telegram_id {telegram_id}: {str(e)}")
            raise
    
    async def get_or_create_user(self, telegram_id: int, username: str = None) -> User:
        """Get existing user or create a new unregistered user"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if not user:
            user = await self.repository.create(
                telegram_id=telegram_id,
                username=username or "",
                number="",
                area=1,  # Default area
                id_number="",
                approved=False
            )
            auth_logger.info(f"Created new unregistered user: {telegram_id}")
        
        return user
    
    async def is_user_registered(self, telegram_id: int) -> bool:
        """Check if user is fully registered"""
        user = await self.get_user_by_telegram_id(telegram_id)
        return user is not None and user.approved
    
    async def validate_registration_data(
        self,
        full_name: str,
        city: str,
        area: str,
        national_id: str,
        phone: str
    ) -> Tuple[bool, dict, dict]:
        """
        Validate all registration data
        Returns: (is_valid, validated_data, errors)
        """
        validated_data = {}
        errors = {}
        
        # Validate name
        is_valid_name, normalized_name = InputValidator.validate_persian_name(full_name)
        if is_valid_name:
            validated_data['full_name'] = normalized_name
        else:
            errors['full_name'] = "نام وارد شده معتبر نیست"
        
        # Validate city
        is_valid_city, normalized_city = InputValidator.validate_city(city, ["تهران"])
        if is_valid_city:
            validated_data['city'] = normalized_city
        else:
            errors['city'] = "شهر وارد شده معتبر نیست"
        
        # Validate area
        is_valid_area, normalized_area = InputValidator.validate_area_code(area)
        if is_valid_area:
            validated_data['area'] = int(normalized_area)
        else:
            errors['area'] = "منطقه وارد شده معتبر نیست"
        
        # Validate national ID
        is_valid_id, normalized_id = InputValidator.validate_national_id(national_id)
        if is_valid_id:
            validated_data['id_number'] = normalized_id
        else:
            errors['id_number'] = "کد ملی وارد شده معتبر نیست"
        
        # Validate phone
        is_valid_phone, normalized_phone = InputValidator.validate_phone_number(phone)
        if is_valid_phone:
            validated_data['number'] = normalized_phone
        else:
            errors['number'] = "شماره موبایل وارد شده معتبر نیست"
        
        # Check for duplicate phone number
        if is_valid_phone:
            existing_user = await self.repository.get_by_field("number", normalized_phone)
            if existing_user:
                errors['number'] = "این شماره موبایل قبلاً ثبت شده است"
        
        # Check for duplicate national ID
        if is_valid_id:
            existing_user = await self.repository.get_by_field("id_number", normalized_id)
            if existing_user:
                errors['id_number'] = "این کد ملی قبلاً ثبت شده است"
        
        is_valid = len(errors) == 0
        return is_valid, validated_data, errors
    
    async def complete_registration(
        self,
        telegram_id: int,
        username: str,
        full_name: str,
        city: str,
        area: str,
        national_id: str,
        phone: str
    ) -> User:
        """Complete user registration after OTP verification"""
        
        # Validate all data
        is_valid, validated_data, errors = await self.validate_registration_data(
            full_name, city, area, national_id, phone
        )
        
        if not is_valid:
            raise ValidationException(
                message=f"Registration validation failed: {errors}",
                user_message="اطلاعات وارد شده معتبر نیست"
            )
        
        # Get or create user
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user:
            # Update existing user
            user.username = username
            user.full_name = validated_data['full_name']
            user.city = validated_data['city']
            user.area = validated_data['area']
            user.id_number = validated_data['id_number']
            user.number = validated_data['number']
            user.approved = True
            
            # Save using repository
            user = await self.repository.update(
                user.id,
                username=username,
                full_name=validated_data['full_name'],
                city=validated_data['city'],
                area=validated_data['area'],
                id_number=validated_data['id_number'],
                number=validated_data['number'],
                approved=True
            )
        else:
            # Create new user
            user = await self.repository.create(
                telegram_id=telegram_id,
                username=username,
                full_name=validated_data['full_name'],
                city=validated_data['city'],
                area=validated_data['area'],
                id_number=validated_data['id_number'],
                number=validated_data['number'],
                approved=True
            )
        
        auth_logger.info(f"User registration completed: {telegram_id}")
        return user
    
    async def get_user_orders_count(self, user_id: int) -> int:
        """Get number of orders for a user"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        return await user.orders.count()
    
    async def update_user_info(self, telegram_id: int, **kwargs) -> User:
        """Update user information"""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            raise UserNotFoundException(telegram_id)
        
        # Filter allowed fields
        allowed_fields = ['username', 'full_name', 'city']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if update_data:
            user = await self.repository.update(user.id, **update_data)
            auth_logger.info(f"Updated user info for {telegram_id}: {list(update_data.keys())}")
        
        return user
    
    async def require_registered_user(self, telegram_id: int) -> User:
        """Get user and ensure they are registered, raise exception if not"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if not user:
            raise UserNotFoundException(telegram_id)
        
        if not user.approved:
            raise UserNotRegisteredException(telegram_id)
        
        return user
    
    async def get_user_stats(self) -> dict:
        """Get user statistics"""
        total_users = await self.repository.count()
        registered_users = len(await self.repository.find(approved=True))
        
        return {
            'total_users': total_users,
            'registered_users': registered_users,
            'unregistered_users': total_users - registered_users,
            'registration_rate': (registered_users / total_users * 100) if total_users > 0 else 0
        }


# Global user service instance
user_service = UserService()
