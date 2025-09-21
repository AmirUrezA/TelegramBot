# 🐳 Docker Deployment Guide

## Enterprise Telegram Bot - Docker Setup

This guide covers running the enterprise Telegram bot using Docker and Docker Compose.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- At least 5GB disk space

## 🚀 Quick Start

### 1. **Basic Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd telegram-bot

# Create environment file
cp env.example .env
nano .env  # Configure your values

# Start the bot
docker-compose up -d
```

### 2. **With Database Migration**
```bash
# Run migration first
docker-compose --profile migration up migration

# Then start the bot
docker-compose up -d bot db
```

## 🔧 Configuration

### **Environment Variables**
Create `.env` file with required values:
```bash
# Required
BOT_TOKEN=your_bot_token
KAVENEGAR_API_KEY=your_sms_key

# Database (optional - uses defaults)
POSTGRES_DB=telegram_bot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/app/logs/bot.log
```

### **Service Profiles**
Use Docker Compose profiles to control which services run:

```bash
# Basic setup (bot + database)
docker-compose up -d

# With development tools
docker-compose --profile development up -d

# With Redis caching
docker-compose --profile with-redis up -d

# With monitoring
docker-compose --profile monitoring up -d

# All services
docker-compose --profile development --profile with-redis --profile monitoring up -d
```

## 📊 Available Services

| Service | Description | Profile | Port |
|---------|-------------|---------|------|
| **bot** | Main Telegram bot | default | - |
| **db** | PostgreSQL database | default | 5432 |
| **migration** | Database migrations | migration | - |
| **pgadmin** | Database admin UI | development | 5050 |
| **redis** | Redis cache | with-redis | 6379 |
| **prometheus** | Monitoring | monitoring | 9090 |

## 🔍 Management Commands

### **Service Management**
```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# View logs
docker-compose logs -f bot
docker-compose logs -f db

# Restart bot only
docker-compose restart bot

# Check service status
docker-compose ps
```

### **Database Operations**
```bash
# Run database migrations
docker-compose --profile migration up migration

# Connect to database
docker-compose exec db psql -U postgres -d telegram_bot

# Backup database
docker-compose exec db pg_dump -U postgres telegram_bot > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres telegram_bot < backup.sql
```

### **Bot Management**
```bash
# View bot logs
docker-compose logs -f bot

# Enter bot container
docker-compose exec bot bash

# Check bot health
docker-compose exec bot python -c "from app.config.settings import config; config.validate()"

# Restart bot with new code
docker-compose build bot
docker-compose up -d bot
```

## 📈 Monitoring & Debugging

### **Health Checks**
All services include health checks:
```bash
# Check all service health
docker-compose ps

# Check specific service
docker inspect enterprise_telegram_bot --format='{{.State.Health.Status}}'
```

### **Logs and Debugging**
```bash
# View real-time logs
docker-compose logs -f --tail=100 bot

# Export logs
docker-compose logs --no-color bot > bot_logs.txt

# Debug database connections
docker-compose exec bot python -c "
from app.services.database import db_service
import asyncio
async def test(): 
    db_service.initialize()
    print('Database connection: OK')
asyncio.run(test())
"
```

### **Resource Monitoring**
```bash
# View resource usage
docker stats enterprise_telegram_bot enterprise_postgres_db

# View volume usage
docker system df
```

## 🔒 Security

### **Network Security**
- Services communicate via isolated Docker network
- Database not exposed externally by default
- Non-root user in containers

### **Environment Security**
```bash
# Secure .env file
chmod 600 .env

# Don't commit sensitive data
echo ".env" >> .gitignore
```

### **Database Security**
```bash
# Change default passwords
export POSTGRES_PASSWORD="$(openssl rand -base64 32)"
export PGADMIN_PASSWORD="$(openssl rand -base64 16)"
```

## ⚡ Performance Optimization

### **Resource Limits**
Services have predefined resource limits:
- **Bot**: 512MB RAM limit, 256MB reservation
- **Database**: 1GB RAM limit, 512MB reservation
- **Redis**: 256MB RAM limit

### **Database Tuning**
Custom PostgreSQL configuration in `postgresql.conf`:
- Optimized for bot workload
- Connection pooling
- Performance monitoring enabled

### **Volume Optimization**
```bash
# Clean up unused volumes
docker volume prune

# Clean up unused images
docker image prune

# Full system cleanup
docker system prune -a
```

## 🔄 Updates & Maintenance

### **Updating the Bot**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build bot
docker-compose up -d bot

# Run any new migrations
docker-compose --profile migration up migration
```

### **Database Maintenance**
```bash
# Analyze database performance
docker-compose exec db psql -U postgres -d telegram_bot -c "ANALYZE;"

# Check database size
docker-compose exec db psql -U postgres -d telegram_bot -c "
SELECT pg_size_pretty(pg_database_size('telegram_bot')) as db_size;
"

# Vacuum database
docker-compose exec db psql -U postgres -d telegram_bot -c "VACUUM ANALYZE;"
```

### **Log Rotation**
Logs are automatically rotated by Docker:
- Bot logs: 50MB max, 5 files kept
- Database logs: Built-in PostgreSQL rotation

## 🚨 Troubleshooting

### **Common Issues**

1. **Bot won't start**
   ```bash
   # Check configuration
   docker-compose exec bot python -c "from app.config.settings import config; config.validate()"
   
   # Check logs
   docker-compose logs bot
   ```

2. **Database connection errors**
   ```bash
   # Check database health
   docker-compose exec db pg_isready -U postgres
   
   # Test connection
   docker-compose exec bot python -c "
   from app.services.database import db_service
   import asyncio
   async def test():
       db_service.initialize()
       async with db_service.get_session() as session:
           result = await session.execute('SELECT 1')
           print('Database OK:', result.scalar())
   asyncio.run(test())
   "
   ```

3. **Out of memory**
   ```bash
   # Check memory usage
   docker stats --no-stream
   
   # Increase swap or reduce resource limits in docker-compose.yml
   ```

4. **Port conflicts**
   ```bash
   # Check what's using ports
   netstat -tlnp | grep :5432
   
   # Change ports in docker-compose.yml
   ```

### **Debug Mode**
```bash
# Run with debug logging
LOG_LEVEL=DEBUG docker-compose up bot

# Run bot directly for debugging
docker-compose run --rm bot python -c "
from app.main import main
import asyncio
asyncio.run(main())
"
```

## 📱 Production Deployment

### **Production Setup**
```bash
# Use production environment
cp env.example .env.production

# Secure configuration
chmod 600 .env.production

# Deploy with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### **Backup Strategy**
```bash
# Daily database backup
docker-compose exec db pg_dump -U postgres telegram_bot | gzip > "backup-$(date +%Y%m%d).sql.gz"

# Backup application data
docker run --rm -v bot_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

Your enterprise bot is now ready for Docker deployment! 🚀
