"""
Enterprise Configuration Management System
Centralized configuration with validation and environment variable support
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    echo_queries: bool = False
    pool_size: int = 10
    pool_overflow: int = 20
    pool_timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables"""
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:amir@db:5432/mybot")
        
        # Ensure asyncpg driver
        if not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            
        return cls(
            url=url,
            echo_queries=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            pool_overflow=int(os.getenv("DB_POOL_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30"))
        )


@dataclass
class TelegramConfig:
    """Telegram bot configuration settings"""
    bot_token: str
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_port: int = 8443
    admin_username: str = "Arshya_Alaee"
    
    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        """Create Telegram config from environment variables"""
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
            
        api_id_str = os.getenv("API_ID")
        api_id = int(api_id_str) if api_id_str else None
        
        return cls(
            bot_token=bot_token,
            api_id=api_id,
            api_hash=os.getenv("API_HASH"),
            webhook_url=os.getenv("WEBHOOK_URL"),
            webhook_port=int(os.getenv("WEBHOOK_PORT", "8443")),
            admin_username=os.getenv("ADMIN_USERNAME", "Arshya_Alaee")
        )


@dataclass 
class SMSConfig:
    """SMS service configuration settings"""
    kavenegar_api_key: str
    verify_template: str = "verify"
    
    @classmethod
    def from_env(cls) -> 'SMSConfig':
        """Create SMS config from environment variables"""
        api_key = os.getenv("KAVENEGAR_API_KEY")
        if not api_key:
            raise ValueError("KAVENEGAR_API_KEY environment variable is required")
            
        return cls(
            kavenegar_api_key=api_key,
            verify_template=os.getenv("SMS_VERIFY_TEMPLATE", "verify")
        )


@dataclass
class PaymentConfig:
    """Payment configuration settings"""
    card_number: str
    card_holder_name: str
    
    @classmethod
    def from_env(cls) -> 'PaymentConfig':
        """Create payment config from environment variables"""
        return cls(
            card_number=os.getenv("PAYMENT_CARD_NUMBER", "6063731181415549"),
            card_holder_name=os.getenv("PAYMENT_CARD_HOLDER", "محمد مهدی مقدم اصل")
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create logging config from environment variables"""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    max_otp_attempts: int = 3
    otp_expiry_minutes: int = 10
    rate_limit_per_minute: int = 60
    allowed_cities: list = None
    
    def __post_init__(self):
        if self.allowed_cities is None:
            self.allowed_cities = ["تهران"]
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create security config from environment variables"""
        allowed_cities_str = os.getenv("ALLOWED_CITIES", "تهران")
        allowed_cities = [city.strip() for city in allowed_cities_str.split(",")]
        
        return cls(
            max_otp_attempts=int(os.getenv("MAX_OTP_ATTEMPTS", "3")),
            otp_expiry_minutes=int(os.getenv("OTP_EXPIRY_MINUTES", "10")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            allowed_cities=allowed_cities
        )


class ApplicationConfig:
    """Main application configuration container"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.telegram = TelegramConfig.from_env()
        self.sms = SMSConfig.from_env()
        self.payment = PaymentConfig.from_env()
        self.logging = LoggingConfig.from_env()
        self.security = SecurityConfig.from_env()
    
    def validate(self) -> None:
        """Validate all configuration settings"""
        # Validate required fields
        if not self.telegram.bot_token:
            raise ValueError("Telegram bot token is required")
        if not self.sms.kavenegar_api_key:
            raise ValueError("Kavenegar API key is required")
        if not self.database.url:
            raise ValueError("Database URL is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (for logging/debugging)"""
        return {
            "database": {
                "url": "***HIDDEN***",  # Don't log sensitive data
                "echo_queries": self.database.echo_queries,
                "pool_size": self.database.pool_size,
            },
            "telegram": {
                "bot_token": "***HIDDEN***",
                "api_id": self.telegram.api_id,
                "webhook_url": self.telegram.webhook_url,
                "admin_username": self.telegram.admin_username,
            },
            "sms": {
                "api_key": "***HIDDEN***",
                "verify_template": self.sms.verify_template,
            },
            "payment": {
                "card_number": self.payment.card_number,
                "card_holder_name": self.payment.card_holder_name,
            },
            "security": {
                "max_otp_attempts": self.security.max_otp_attempts,
                "otp_expiry_minutes": self.security.otp_expiry_minutes,
                "allowed_cities": self.security.allowed_cities,
            }
        }


# Global configuration instance
config = ApplicationConfig()
