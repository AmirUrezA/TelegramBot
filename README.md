# 🚀 Enterprise Telegram Bot

**A professional, enterprise-level Telegram bot for educational product sales with advanced features and clean architecture.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/database-postgresql-blue.svg)](https://www.postgresql.org/)
[![Enterprise Architecture](https://img.shields.io/badge/architecture-enterprise-green.svg)]()
[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

## ✨ Features

### 🏗️ **Enterprise Architecture**
- **Modular Design**: Separated into services, handlers, models, and utilities
- **Dependency Injection**: Clean, testable code with proper DI
- **Service Layer Pattern**: Business logic separated from presentation
- **Repository Pattern**: Abstracted database operations
- **Middleware Support**: Error handling, validation, and logging middleware

### 🛒 **Product Management**
- Browse products by educational grade (5th to 12th grade)
- Filter by academic major (Math, Science, Humanities)
- Detailed product information and pricing
- Installment payment support for high school products

### 🎫 **Advanced Referral System**
- Seller-linked referral codes for tracking
- Grade-specific referral codes
- Installment eligibility control
- Usage tracking and limits
- Sales analytics for sellers

### 👤 **User Management & Security**
- Complete user registration with OTP verification
- Persian input validation and sanitization
- National ID and phone number verification
- User approval workflow
- Session management

### 💳 **Payment & Orders**
- Multiple payment methods (cash/installment)
- Receipt upload and verification
- Order tracking and status management
- Automated admin notifications
- Installment payment tracking

### 🎲 **Additional Features**
- **Lottery System**: User participation with OTP verification
- **CRM Integration**: Consultation request management
- **Cooperation Module**: Job application processing
- **Multi-language Support**: Full Persian language support
- **Admin Notifications**: Real-time Telegram notifications

### 🔧 **Technical Features**
- **Async/Await**: Full asynchronous operation
- **Connection Pooling**: Optimized database performance  
- **Error Handling**: Comprehensive exception management
- **Input Validation**: Persian text and phone number validation
- **Logging**: Enterprise-level logging with rotation
- **Testing**: Full test suite with fixtures and mocks

## 🏗️ **Architecture Overview**

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

### 📁 **Directory Structure**
```
app/
├── config/          # Configuration management
├── constants/       # Centralized constants  
├── exceptions/      # Custom exception classes
├── handlers/        # Conversation handlers
├── middleware/      # Error handling & validation
├── models/          # Database models
├── services/        # Business logic layer
├── utils/          # Utilities and helpers
└── main.py         # Application entry point
```

## 🚀 **Quick Start**

### 1. **Environment Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd telegram-bot

# Install dependencies
pip install -r app/requirements.txt

# Setup environment variables
cp env.example .env
nano .env  # Configure your values
```

### 2. **Database Setup**
```bash
# Run database migrations
alembic upgrade head

# Verify tables
python verify_tables.py
```

### 3. **Run the Bot**
```bash
# Development mode
python run_bot.py

# Or run directly
python -m app.main
```

### 4. **Environment Variables**
Required variables in `.env`:
```bash
BOT_TOKEN=your_telegram_bot_token
KAVENEGAR_API_KEY=your_sms_api_key  
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Optional
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
LOG_LEVEL=INFO
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file  
pytest tests/test_validation.py -v
```

## 📊 **Key Benefits**

| Feature | Before Refactoring | After Refactoring |
|---------|-------------------|-------------------|
| **Code Organization** | Single 1,688-line file | 25+ organized modules |
| **Maintainability** | Difficult to modify | Easy to extend and maintain |
| **Testing** | Hard to test | Full test coverage |
| **Error Handling** | Basic try/catch | Enterprise exception hierarchy |
| **Configuration** | Hardcoded values | Environment-based configuration |
| **Logging** | Basic logging | Enterprise logging with rotation |
| **Database** | Direct SQLAlchemy | Service layer with repositories |
| **Performance** | No optimization | Connection pooling & async ops |

## 🔧 **Production Deployment**

The bot is production-ready with:

- ✅ **Systemd Service Configuration**
- ✅ **Nginx Proxy Setup** 
- ✅ **Database Connection Pooling**
- ✅ **Automatic Log Rotation**
- ✅ **Health Monitoring**
- ✅ **Security Hardening**
- ✅ **Backup Strategies**

See [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📚 **Documentation**

- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) - Complete API reference
- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) - Production deployment guide  
- [`REFACTORING_SUMMARY.md`](REFACTORING_SUMMARY.md) - Refactoring details

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 **Support**

- 📧 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)  
- 📚 **Documentation**: See docs folder for detailed guides

## 🌟 **Acknowledgments**

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Database powered by [PostgreSQL](https://www.postgresql.org/)
- SMS service by [Kavenegar](https://kavenegar.com/)
- Async database operations with [SQLAlchemy](https://www.sqlalchemy.org/)

---

**🚀 Ready for enterprise deployment with professional architecture and best practices!** 
*Note: The project refactored via sonnet-4*