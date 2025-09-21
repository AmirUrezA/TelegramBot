#!/bin/bash
# Docker Test Script for Enterprise Telegram Bot
# This script tests the Docker setup and validates the configuration

set -e

echo "🐳 Testing Docker Setup for Enterprise Telegram Bot"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check prerequisites
echo "🔍 Checking Prerequisites..."

# Check Docker
docker --version > /dev/null 2>&1
print_status "Docker is installed"

# Check Docker Compose
docker-compose --version > /dev/null 2>&1
print_status "Docker Compose is installed"

# Check if .env exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from env.example..."
    cp env.example .env
    echo "📝 Please edit .env with your actual values before running the bot"
fi

# Check environment file
source .env
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    print_warning "BOT_TOKEN not configured in .env"
fi

if [ -z "$KAVENEGAR_API_KEY" ] || [ "$KAVENEGAR_API_KEY" = "your_kavenegar_api_key_here" ]; then
    print_warning "KAVENEGAR_API_KEY not configured in .env"
fi

print_status "Environment file validation completed"

# Test Docker build
echo -e "\n🏗️  Testing Docker Build..."
docker-compose build bot > /dev/null 2>&1
print_status "Docker build successful"

# Test database startup
echo -e "\n🗄️  Testing Database Startup..."
docker-compose up -d db
sleep 10

# Wait for database to be healthy
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo -e "${RED}❌ Database failed to start within ${timeout}s${NC}"
    docker-compose logs db
    exit 1
fi

print_status "Database startup successful"

# Test database migration
echo -e "\n📊 Testing Database Migration..."
docker-compose --profile migration up migration > /dev/null 2>&1
print_status "Database migration successful"

# Test bot configuration validation
echo -e "\n⚙️  Testing Bot Configuration..."
docker-compose run --rm bot python -c "from app.config.settings import config; config.validate(); print('Configuration valid')" > /dev/null 2>&1
print_status "Bot configuration validation successful"

# Test database connection from bot
echo -e "\n🔗 Testing Database Connection from Bot..."
docker-compose run --rm bot python -c "
from app.services.database import db_service
import asyncio
async def test():
    db_service.initialize()
    async with db_service.get_session() as session:
        result = await session.execute('SELECT 1 as test')
        assert result.scalar() == 1
        print('Database connection successful')
asyncio.run(test())
" > /dev/null 2>&1
print_status "Database connection test successful"

# Test bot startup (without actually running)
echo -e "\n🤖 Testing Bot Initialization..."
timeout 10s docker-compose run --rm bot python -c "
from app.main import TelegramBotApplication
import asyncio
async def test():
    app = TelegramBotApplication()
    await app.initialize()
    print('Bot initialization successful')
    await app.shutdown()
asyncio.run(test())
" > /dev/null 2>&1
print_status "Bot initialization test successful"

# Clean up test containers
echo -e "\n🧹 Cleaning up..."
docker-compose down > /dev/null 2>&1
print_status "Cleanup completed"

# Summary
echo -e "\n🎉 Docker Setup Test Results"
echo "============================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "Your Docker setup is ready. You can now:"
echo "1. Edit .env with your actual tokens"
echo "2. Run: docker-compose up -d"
echo "3. Check logs: docker-compose logs -f bot"
echo ""
print_info "For more information, see DOCKER_GUIDE.md"
