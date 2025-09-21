# 📚 API Documentation

## Enterprise Telegram Bot API Reference

This document provides detailed information about the bot's architecture, services, and APIs.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │◄──►│   Bot Handlers   │◄──►│   Services      │
│   Updates       │    │   (Controllers)  │    │   (Business)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Middleware     │    │   Database      │
                       │   (Validation)   │    │   (Models)      │
                       └──────────────────┘    └─────────────────┘
```

## 🔧 Services API

### UserService

#### Methods

**`async get_user_by_telegram_id(telegram_id: int) -> Optional[User]`**
- Get user by Telegram ID
- Returns `None` if user not found

**`async complete_registration(telegram_id, username, full_name, city, area, national_id, phone) -> User`**
- Complete user registration process
- Validates all input data
- Creates or updates user record
- Throws `ValidationException` on invalid data

**`async is_user_registered(telegram_id: int) -> bool`**
- Check if user is fully registered
- Returns `True` if user exists and is approved

**`async require_registered_user(telegram_id: int) -> User`**
- Get user and ensure they are registered
- Throws `UserNotFoundException` if user doesn't exist
- Throws `UserNotRegisteredException` if user not approved

### SMSService

#### Methods

**`generate_otp(length: int = 4) -> str`**
- Generate random OTP code
- Default length is 4 digits

**`async send_otp(phone_number: str, otp: str, template: Optional[str] = None) -> dict`**
- Send OTP SMS using Kavenegar
- Uses configured template by default
- Throws `SMSException` on failure

**`async send_custom_message(phone_number: str, message: str, sender: Optional[str] = None) -> dict`**
- Send custom SMS message
- Optional sender parameter

### NotificationService

#### Methods

**`async send_to_admin(message: str, parse_mode: str = None) -> bool`**
- Send notification to admin via Telegram
- Supports Markdown/HTML parse modes

**`async send_order_notification(order_id, user_id, username, product_name, final_price, payment_type, referral_code) -> bool`**
- Send new order notification to admin
- Includes all order details

**`async send_cooperation_notification(telegram_id, username, phone, city, resume_text) -> bool`**
- Send cooperation application notification

### DatabaseService

#### Methods

**`initialize() -> None`**
- Initialize database engine and session maker

**`async get_session() -> AsyncSession`**
- Get async database session (context manager)
- Handles automatic rollback on exceptions

**`async create_tables() -> None`**
- Create all database tables

## 🗃️ Models API

### User Model

#### Properties
- `telegram_id: int` - Unique Telegram user ID
- `username: str` - Telegram username
- `full_name: str` - Full name in Persian
- `number: str` - Phone number
- `area: int` - Educational area code
- `id_number: str` - National ID
- `city: str` - City name
- `approved: bool` - Registration approval status

#### Methods
- `is_registered -> bool` - Check if fully registered
- `to_dict() -> dict` - Convert to dictionary (safe for JSON)

### Product Model

#### Properties
- `name: str` - Product name
- `grade: GradeEnum` - Educational grade
- `major: MajorEnum` - Academic major
- `description: str` - Product description
- `price: int` - Price in Tomans
- `is_active: bool` - Active status

#### Methods
- `formatted_price -> str` - Get formatted price string
- `grade_persian -> str` - Get Persian grade name
- `major_persian -> str` - Get Persian major name

### Order Model

#### Properties
- `user_id: int` - Foreign key to User
- `product_id: int` - Foreign key to Product
- `status: OrderStatusEnum` - Order status
- `installment: bool` - Is installment payment
- `seller_id: int` - Associated seller ID for tracking
- `final_price: int` - Final price (equals product price)
- `first_installment: DateTime` - First payment date
- `second_installment: DateTime` - Second payment date
- `third_installment: DateTime` - Third payment date

#### Methods
- `is_installment_complete -> bool` - Check if all installments paid
- `paid_installments_count -> int` - Count paid installments
- `installment_amount -> int` - Get installment amount
- `get_installment_status(index: int) -> dict` - Get installment status

## 🎯 Handlers API

### MenuHandler

#### Methods
**`async start(update, context)`**
- Show main menu
- Handle deep links (cooperation, lottery)
- Clear user context

**`async handle_reply_keyboard_button(update, context)`**
- Handle reply keyboard button presses
- Route to appropriate handlers

### RegistrationHandler

#### Constructor
`RegistrationHandler(user_service, sms_service, notification_service)`

#### Conversation Flow
1. `ask_name` → ASK_NAME
2. `handle_name` → ASK_CITY
3. `handle_city` → ASK_AREA
4. `handle_area` → ASK_ID
5. `handle_id` → ASK_PHONE
6. `handle_phone` → ASK_OTP
7. `handle_otp` → END (complete registration)

### PaymentHandler

#### Constructor
`PaymentHandler(user_service, notification_service)`

#### Conversation Flow
1. `start_purchase` → ASK_REFERRAL_CODE
2. `handle_referral_code_input` → ASK_PAYMENT_METHOD (conditional)
3. `handle_payment_method` → ASK_PAYMENT_PROOF
4. `handle_payment_proof` → END (complete order)

## 🔒 Security API

### Validation Utilities

#### InputValidator Methods

**`validate_persian_name(name: str) -> Tuple[bool, str]`**
- Validates Persian name (2-5 words, Persian characters only)
- Returns (is_valid, normalized_name)

**`validate_phone_number(phone: str) -> Tuple[bool, str]`**
- Validates Iranian mobile numbers (09xxxxxxxxx)
- Handles Persian digit conversion
- Returns (is_valid, normalized_phone)

**`validate_national_id(national_id: str) -> Tuple[bool, str]`**
- Validates Iranian national ID (10 digits)
- Rejects sequential numbers
- Returns (is_valid, normalized_id)

**`validate_otp(otp: str, expected_otp: str) -> Tuple[bool, str]`**
- Validates OTP against expected value
- Handles Persian digit conversion
- Returns (is_valid, normalized_otp)

## 🚨 Exception Handling

### Exception Hierarchy

```
BotException (base)
├── ValidationException
├── UserNotFoundException  
├── UserNotRegisteredException
├── ProductNotFoundException
├── SMSException
├── DatabaseException
├── PaymentException
├── LotteryException
├── CooperationException
└── NotificationException
```

### Exception Properties
- `message: str` - Technical error message
- `error_code: str` - Unique error code
- `user_message: str` - User-friendly message (Persian)
- `context: dict` - Additional error context

## 📊 Configuration API

### ApplicationConfig

#### Sections
- `database: DatabaseConfig` - Database settings
- `telegram: TelegramConfig` - Bot configuration  
- `sms: SMSConfig` - SMS service settings
- `payment: PaymentConfig` - Payment information
- `logging: LoggingConfig` - Log configuration
- `security: SecurityConfig` - Security settings

#### Methods
- `validate() -> None` - Validate all configuration
- `to_dict() -> dict` - Export config (safe, masks secrets)

## 🔄 Conversation States

### State Constants
```python
# Registration States
ASK_NAME = 1
ASK_CITY = 2
ASK_AREA = 3
ASK_ID = 4
ASK_PHONE = 5
ASK_OTP = 6

# Payment States  
ASK_REFERRAL_CODE = 100
ASK_PAYMENT_METHOD = 101
ASK_PAYMENT_PROOF = 102

# And more...
```

## 📝 Usage Examples

### Creating a New Service

```python
from app.services.database import BaseRepository, db_service
from app.models import MyModel

class MyService:
    def __init__(self):
        self.repository = BaseRepository(MyModel, db_service)
    
    async def create_item(self, **kwargs):
        return await self.repository.create(**kwargs)
    
    async def get_item(self, id: int):
        return await self.repository.get_by_id(id)
```

### Adding a New Handler

```python
from app.handlers.base import BaseHandler
from app.middleware.error_handler import handle_exceptions

class MyHandler:
    def __init__(self, my_service):
        self.service = my_service
    
    @handle_exceptions()
    async def handle_message(self, update, context):
        # Handler logic here
        pass
```

### Custom Validation

```python
from app.utils.validation import InputValidator

def validate_custom_field(value: str) -> Tuple[bool, str]:
    # Custom validation logic
    if not value or len(value) < 3:
        return False, ""
    
    return True, value.strip()
```

## 🧪 Testing API

### Test Fixtures

```python
@pytest.fixture
async def user_service(db_service):
    return UserService()

@pytest.fixture  
def sample_user_data():
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "full_name": "تست کاربر",
        # ... more fields
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest --cov=app

# Run with verbose output
pytest -v
```

This API documentation provides a comprehensive reference for developers working with the enterprise Telegram bot architecture. 🚀
