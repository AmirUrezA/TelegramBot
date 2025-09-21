"""
Custom Exception Classes
Enterprise-level exception handling with proper error categorization
"""

from typing import Optional, Dict, Any


class BotException(Exception):
    """Base exception for all bot-related errors"""
    
    def __init__(
        self, 
        message: str,
        error_code: Optional[str] = None,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.user_message = user_message or "خطا در پردازش درخواست"
        self.context = context or {}


class ValidationException(BotException):
    """Exception for input validation errors"""
    
    def __init__(
        self, 
        message: str,
        field_name: Optional[str] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        self.field_name = field_name
        context = {"field_name": field_name} if field_name else {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            user_message=user_message or "اطلاعات وارد شده معتبر نیست",
            context=context
        )


class UserNotFoundException(BotException):
    """Exception when user is not found"""
    
    def __init__(self, user_id: int, **kwargs):
        super().__init__(
            message=f"User with ID {user_id} not found",
            error_code="USER_NOT_FOUND",
            user_message="کاربر یافت نشد. لطفا ابتدا ثبت نام کنید",
            context={"user_id": user_id}
        )


class UserNotRegisteredException(BotException):
    """Exception when user is not registered"""
    
    def __init__(self, user_id: int, **kwargs):
        super().__init__(
            message=f"User with ID {user_id} is not registered",
            error_code="USER_NOT_REGISTERED",
            user_message="شما هنوز ثبت نام نکردید",
            context={"user_id": user_id}
        )


class ProductNotFoundException(BotException):
    """Exception when product is not found"""
    
    def __init__(self, product_id: Optional[int] = None, product_name: Optional[str] = None, **kwargs):
        context = {}
        if product_id:
            context["product_id"] = product_id
        if product_name:
            context["product_name"] = product_name
            
        super().__init__(
            message=f"Product not found: ID={product_id}, Name={product_name}",
            error_code="PRODUCT_NOT_FOUND",
            user_message="محصول مورد نظر یافت نشد",
            context=context
        )


class OrderNotFoundException(BotException):
    """Exception when order is not found"""
    
    def __init__(self, order_id: int, **kwargs):
        super().__init__(
            message=f"Order with ID {order_id} not found",
            error_code="ORDER_NOT_FOUND",
            user_message="سفارش مورد نظر یافت نشد",
            context={"order_id": order_id}
        )


class ReferralCodeException(BotException):
    """Exception for referral code related errors"""
    
    def __init__(self, code: str, message: str = None, **kwargs):
        super().__init__(
            message=message or f"Invalid referral code: {code}",
            error_code="INVALID_REFERRAL_CODE",
            user_message="کد معرف معتبر نیست",
            context={"referral_code": code}
        )


class SMSException(BotException):
    """Exception for SMS service errors"""
    
    def __init__(self, phone_number: str, error_details: str, **kwargs):
        super().__init__(
            message=f"SMS sending failed for {phone_number}: {error_details}",
            error_code="SMS_ERROR",
            user_message=f"خطا در ارسال پیامک: {error_details}",
            context={"phone_number": phone_number, "error_details": error_details}
        )


class PaymentException(BotException):
    """Exception for payment related errors"""
    
    def __init__(self, message: str, payment_context: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="PAYMENT_ERROR",
            user_message="خطا در پردازش پرداخت",
            context=payment_context or {}
        )


class DatabaseException(BotException):
    """Exception for database related errors"""
    
    def __init__(self, operation: str, error_details: str, **kwargs):
        super().__init__(
            message=f"Database error in {operation}: {error_details}",
            error_code="DATABASE_ERROR",
            user_message="خطا در دسترسی به اطلاعات",
            context={"operation": operation, "error_details": error_details}
        )


class LotteryException(BotException):
    """Exception for lottery related errors"""
    
    def __init__(self, lottery_id: Optional[int] = None, message: str = None, **kwargs):
        context = {"lottery_id": lottery_id} if lottery_id else {}
        super().__init__(
            message=message or f"Lottery error for ID {lottery_id}",
            error_code="LOTTERY_ERROR",
            user_message="خطا در قرعه کشی",
            context=context
        )


class CooperationException(BotException):
    """Exception for cooperation application errors"""
    
    def __init__(self, user_id: int, message: str = None, **kwargs):
        super().__init__(
            message=message or f"Cooperation application error for user {user_id}",
            error_code="COOPERATION_ERROR",
            user_message="خطا در درخواست همکاری",
            context={"user_id": user_id}
        )


class ConfigurationException(BotException):
    """Exception for configuration errors"""
    
    def __init__(self, config_key: str, message: str = None, **kwargs):
        super().__init__(
            message=message or f"Configuration error for key: {config_key}",
            error_code="CONFIG_ERROR",
            user_message="خطا در پیکربندی سیستم",
            context={"config_key": config_key}
        )


class RateLimitException(BotException):
    """Exception for rate limiting errors"""
    
    def __init__(self, user_id: int, limit_type: str, **kwargs):
        super().__init__(
            message=f"Rate limit exceeded for user {user_id}, type: {limit_type}",
            error_code="RATE_LIMIT_EXCEEDED",
            user_message="تعداد درخواست‌ها بیش از حد مجاز است. لطفا صبر کنید",
            context={"user_id": user_id, "limit_type": limit_type}
        )


class FileUploadException(BotException):
    """Exception for file upload errors"""
    
    def __init__(self, file_id: str, message: str = None, **kwargs):
        super().__init__(
            message=message or f"File upload error for file {file_id}",
            error_code="FILE_UPLOAD_ERROR",
            user_message="خطا در آپلود فایل",
            context={"file_id": file_id}
        )


class NotificationException(BotException):
    """Exception for notification service errors"""
    
    def __init__(self, recipient: str, message: str = None, **kwargs):
        super().__init__(
            message=message or f"Notification error for recipient {recipient}",
            error_code="NOTIFICATION_ERROR",
            user_message="خطا در ارسال اطلاع رسانی",
            context={"recipient": recipient}
        )
