# 🚀 Deployment Guide

## Enterprise Telegram Bot Deployment

This guide covers deploying your enterprise-level Telegram bot to production.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Redis (optional, for caching)
- Reverse proxy (nginx)
- SSL certificate

## 🛠️ Local Development Setup

### 1. Clone and Setup
```bash
# Install dependencies
pip install -r app/requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your values
nano .env
```

### 2. Database Setup
```bash
# Run migrations
alembic upgrade head

# Verify database
python verify_tables.py
```

### 3. Run Bot
```bash
# Development mode
python run_bot.py

# Or run directly
python -m app.main
```

## 🌐 Production Deployment

### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and PostgreSQL
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# Create user
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

### 2. Application Setup

```bash
# Clone repository
git clone <your-repo-url> telegram-bot
cd telegram-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Setup environment
cp env.example .env
nano .env  # Configure production values
```

### 3. Database Configuration

```bash
# Create database
sudo -u postgres createdb telegram_bot
sudo -u postgres createuser botuser
sudo -u postgres psql -c "ALTER USER botuser WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO botuser;"

# Run migrations
alembic upgrade head
```

### 4. Systemd Service

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Enterprise Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/home/botuser/telegram-bot
Environment=PATH=/home/botuser/telegram-bot/venv/bin
ExecStart=/home/botuser/telegram-bot/venv/bin/python run_bot.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/botuser/telegram-bot/logs /home/botuser/telegram-bot/receipts

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot
sudo journalctl -u telegram-bot -f
```

### 6. Nginx Configuration (Optional - for webhooks)

Create `/etc/nginx/sites-available/telegram-bot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring & Logging

### 1. Log Management

```bash
# View logs
sudo journalctl -u telegram-bot -f

# Log rotation is handled by systemd
# Application logs are in logs/bot.log with automatic rotation
```

### 2. Health Monitoring

```bash
# Create health check script
cat > /home/botuser/health_check.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet telegram-bot; then
    echo "Bot service is down!"
    systemctl restart telegram-bot
fi
EOF

chmod +x /home/botuser/health_check.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /home/botuser/health_check.sh
```

### 3. Database Backup

```bash
# Create backup script
cat > /home/botuser/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump telegram_bot > /home/botuser/backups/db_backup_$DATE.sql
# Keep only last 7 days
find /home/botuser/backups -name "db_backup_*.sql" -mtime +7 -delete
EOF

# Add to crontab for daily backups
# 0 2 * * * /home/botuser/backup_db.sh
```

## 🔐 Security Considerations

### 1. Environment Variables
- Never commit `.env` to version control
- Use strong passwords for database
- Rotate API keys regularly

### 2. Database Security
```sql
-- Limit database permissions
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO botuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO botuser;
```

### 3. Firewall Setup
```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 🔧 Maintenance

### 1. Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r app/requirements.txt

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart telegram-bot
```

### 2. Database Maintenance
```bash
# Analyze database performance
psql telegram_bot -c "ANALYZE;"

# Check connection count
psql telegram_bot -c "SELECT count(*) FROM pg_stat_activity;"
```

## 📈 Scaling

### 1. Multiple Workers
```bash
# Run multiple instances with different webhook ports
# Use load balancer (nginx) to distribute load
```

### 2. Redis Caching
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis in .env
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Optimization
- Enable connection pooling
- Add database indexes
- Monitor query performance
- Consider read replicas for heavy loads

## 🚨 Troubleshooting

### Common Issues

1. **Bot not responding**
   ```bash
   sudo journalctl -u telegram-bot -n 100
   ```

2. **Database connection errors**
   ```bash
   sudo -u postgres psql telegram_bot -c "SELECT version();"
   ```

3. **SMS errors**
   - Check Kavenegar API key
   - Verify SMS credit balance

4. **Memory issues**
   ```bash
   # Monitor memory usage
   ps aux | grep python
   free -h
   ```

### Performance Monitoring

```bash
# Monitor system resources
htop

# Check database performance  
psql telegram_bot -c "SELECT * FROM pg_stat_user_tables;"

# Monitor bot logs
tail -f logs/bot.log
```

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] Database created and migrated
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Health checks enabled
- [ ] Service auto-start enabled
- [ ] Security hardening applied

Your enterprise Telegram bot is now ready for production! 🎉
