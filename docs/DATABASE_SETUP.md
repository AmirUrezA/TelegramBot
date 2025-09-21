# 🗄️ Database Setup Guide

## 🎯 Quick Setup for Clean Database

After the enterprise refactoring, follow these steps to set up a clean database.

## 📋 Prerequisites

- PostgreSQL installed and running locally
- Database created (e.g., `mybot`)
- `.env` file configured with correct database credentials

## 🚀 Step 1: Configure Environment

Copy and configure your environment file:
```bash
cp env.example .env
```

Edit `.env` with your database credentials:
```bash
# For local development:
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/mybot

# For Docker (when using docker-compose):
# DATABASE_URL=postgresql+asyncpg://postgres:your_password@db:5432/mybot
```

## 🗑️ Step 2: Clean Database (You Handle This)

As you mentioned, you'll drop all tables manually:

### PostgreSQL Command Line:
```sql
-- Connect to your database
\c mybot

-- Drop all tables
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

### Or using psql command:
```bash
psql -U postgres -d mybot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"
```

## 🔄 Step 3: Clean Migration History

Remove old migration files (backup first):
```bash
# Backup old migrations
mkdir -p alembic/versions_backup
mv alembic/versions/*.py alembic/versions_backup/
```

## 🏗️ Step 4: Generate Fresh Migration

```bash
# Generate new initial migration
python -m alembic revision --autogenerate -m "Initial clean database setup"
```

## ✅ Step 5: Apply Migration

```bash
# Apply the migration
python -m alembic upgrade head
```

## 🔍 Step 6: Verify Setup

Check that all tables were created:
```bash
python -c "
import asyncio
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:amir@localhost:5432/mybot')
sync_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

engine = create_engine(sync_url)
with engine.connect() as conn:
    result = conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\' ORDER BY tablename'))
    tables = [row[0] for row in result]
    print(f'✅ Created {len(tables)} tables:')
    for table in tables:
        print(f'   - {table}')
"
```

## 🎯 Expected Tables

After setup, you should have these tables:
- `alembic_version` - Migration tracking
- `cooperations` - Job applications  
- `crm` - Consultation requests
- `files` - File uploads
- `lotteries` - Lottery system
- `order_receipts` - Order-file junction table
- `orders` - Purchase orders (NO discount field)
- `products` - Product catalog
- `referral_codes` - Referral codes (NO discount field) 
- `sellers` - Seller accounts
- `users` - User accounts
- `users_in_lottery` - Lottery participation

## 🚀 Ready to Go!

After completing these steps:
1. ✅ **Clean database** with fresh schema
2. ✅ **No legacy fields** (discount fields removed)
3. ✅ **Enterprise architecture** fully implemented
4. ✅ **Single migration** for clean history

Your bot is now ready to run with a pristine database!

```bash
# Start the bot
python run_bot.py
```

## 🔧 Troubleshooting

### Connection Error "could not translate host name 'db'"
- ✅ **Fixed!** The env.example now defaults to `localhost` for local development
- Use `db` hostname only when running in Docker

### "No module named 'models'"  
- ✅ **Fixed!** Updated `alembic/env.py` to import from the new `app.models` structure

### Missing psycopg2
```bash
pip install psycopg2-binary
```

The setup is now streamlined and ready for your database reset!
