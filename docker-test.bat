@echo off
REM Docker Test Script for Enterprise Telegram Bot (Windows)
REM This script tests the Docker setup and validates the configuration

echo 🐳 Testing Docker Setup for Enterprise Telegram Bot
echo ==================================================

REM Check prerequisites
echo 🔍 Checking Prerequisites...

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    exit /b 1
)
echo ✅ Docker is installed

REM Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed
    exit /b 1
)
echo ✅ Docker Compose is installed

REM Check if .env exists
if not exist .env (
    echo ⚠️ .env file not found. Creating from env.example...
    copy env.example .env >nul
    echo 📝 Please edit .env with your actual values before running the bot
)

echo ✅ Environment file validation completed

REM Test Docker build
echo.
echo 🏗️ Testing Docker Build...
docker-compose build bot >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)
echo ✅ Docker build successful

REM Test database startup
echo.
echo 🗄️ Testing Database Startup...
docker-compose up -d db >nul 2>&1
timeout /t 10 /nobreak >nul

REM Test database connection
docker-compose exec -T db pg_isready -U postgres >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Database failed to start
    docker-compose logs db
    exit /b 1
)
echo ✅ Database startup successful

REM Test database migration
echo.
echo 📊 Testing Database Migration...
docker-compose --profile migration up migration >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Database migration failed
    exit /b 1
)
echo ✅ Database migration successful

REM Test bot configuration
echo.
echo ⚙️ Testing Bot Configuration...
docker-compose run --rm bot python -c "from app.config.settings import config; config.validate(); print('Configuration valid')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Bot configuration validation failed
    exit /b 1
)
echo ✅ Bot configuration validation successful

REM Clean up
echo.
echo 🧹 Cleaning up...
docker-compose down >nul 2>&1
echo ✅ Cleanup completed

REM Summary
echo.
echo 🎉 Docker Setup Test Results
echo =============================
echo ✅ All tests passed!
echo.
echo Your Docker setup is ready. You can now:
echo 1. Edit .env with your actual tokens
echo 2. Run: docker-compose up -d
echo 3. Check logs: docker-compose logs -f bot
echo.
echo ℹ️ For more information, see DOCKER_GUIDE.md

pause
