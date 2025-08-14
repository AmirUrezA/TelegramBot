# Telegram Bot with Referral Code System

This is a Telegram bot for selling educational products with a referral code system that provides discounts to customers.

## Features

### 🛒 Product Management
- Browse products by grade (5th to 12th grade)
- Filter by major for high school grades (Math, Science, Humanities)
- View product details and prices

### 🎫 Referral Code System
- **With Referral Code**: 10% discount (or custom discount based on code)
- **Without Referral Code**: 5% default discount
- Automatic order creation with discount calculation
- Order tracking with status management

### 👤 User Management
- User registration and approval system
- Order history tracking
- Referral code validation

## Database Schema

### Tables
- **products**: Educational products with grade, major, price
- **users**: Telegram users with approval status
- **orders**: Purchase orders with referral codes and discounts
- **referral_codes**: Discount codes with percentage values
- **sellers**: Product sellers

### Key Features
- **Order tracking**: Each order includes referral code, discount percentage, and final price
- **Flexible discounts**: Referral codes can have different discount percentages
- **Status management**: Orders have pending/approved/rejected status

## Buying Process Flow

1. **User selects product** → Views product details
2. **Clicks "Buy"** → System checks if user is approved
3. **Referral code choice**:
   - "کد معرف دارم" (I have referral code)
   - "کد معرف ندارم" (I don't have referral code - default 5% discount)
4. **If has referral code**:
   - User enters referral code
   - System validates code
   - Applies discount (e.g., 10%, 15%, 20%)
5. **Order creation**:
   - Calculates final price
   - Creates order with referral code and discount info
   - Shows confirmation with price breakdown

## Setup Instructions

### 1. Database Setup
```bash
# Run migrations
alembic upgrade head

# Add sample data
python add_sample_data.py
```

### 2. Environment Variables
Create a `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
```

### 3. Run the Bot
```bash
python telegrambot.py
```

## Sample Referral Codes

After running `add_sample_data.py`, you'll have these test codes:
- `WELCOME10` - 10% discount
- `STUDENT15` - 15% discount  
- `SPECIAL20` - 20% discount

## Testing the System

1. Start the bot
2. Send `/start`
3. Click "📚 محصولات" (Products)
4. Select a grade and major
5. Choose a product
6. Click "🛒 خرید" (Buy)
7. Choose referral code option:
   - Enter a valid code like "WELCOME10"
   - Or choose "کد معرف ندارم" for default discount
8. See order confirmation with price breakdown

## Order Confirmation Example

```
✅ سفارش شما با موفقیت ثبت شد!

📦 محصول: کتاب ریاضی پایه دهم
💰 قیمت اصلی: 150,000 تومان
🎫 کد معرف: WELCOME10
💸 تخفیف: 10%
💵 قیمت نهایی: 135,000 تومان

سفارش شما در حال بررسی است و به زودی با شما تماس خواهیم گرفت.
```

## Technical Implementation

### Key Functions
- `buy_product()`: Initiates buying process
- `handle_referral_code_input()`: Manages referral code flow
- `process_order_with_referral()`: Creates order with referral discount
- `process_order_without_referral()`: Creates order with default discount

### Database Operations
- Referral code validation
- Discount calculation
- Order creation with all relevant data
- Context management for multi-step flows

## Future Enhancements

- Admin panel for managing referral codes
- Analytics dashboard for sales and referral tracking
- Multiple referral codes per user
- Referral code expiration dates
- Commission tracking for sellers 

TESTING CI/CD 6

---

## Host Security: Fail2ban for Dockerized Postgres (Ubuntu 22.04)

This project includes a ready-made setup to ban IPs that brute-force Postgres running in Docker (`postgres_db`). It extracts failed login attempts from Docker logs to a plain text file for Fail2ban.

### Files added
- `docker-compose.yml`: Postgres `command:` set to include client IP in logs
- `scripts/postgres-docker-auth-extract.sh`: Extracts auth failures from Docker logs
- `systemd/pg-fail2ban-extract.service` and `systemd/pg-fail2ban-extract.timer`: Run extractor every minute
- `fail2ban/postgresql.conf`: Custom Fail2ban filter
- `fail2ban/jail.local`: Fail2ban jail watching the extracted log

### One-time host setup (run on Ubuntu 22.04)
```bash
# 1) Ensure Postgres adds client IP to logs and restart db service
cd /path/to/TelegramBotMaze
docker compose up -d --force-recreate db

# 2) Install fail2ban
sudo apt update && sudo apt install -y fail2ban

# 3) Install extractor script and systemd units
sudo install -m 0755 scripts/postgres-docker-auth-extract.sh /usr/local/bin/postgres-docker-auth-extract.sh
sudo install -m 0644 systemd/pg-fail2ban-extract.service /etc/systemd/system/pg-fail2ban-extract.service
sudo install -m 0644 systemd/pg-fail2ban-extract.timer /etc/systemd/system/pg-fail2ban-extract.timer

# 4) Install Fail2ban filter and jail
sudo install -m 0644 fail2ban/postgresql.conf /etc/fail2ban/filter.d/postgresql.conf
sudo install -m 0644 fail2ban/jail.local /etc/fail2ban/jail.local

# 5) Enable timer and Fail2ban
sudo systemctl daemon-reload
sudo systemctl enable --now pg-fail2ban-extract.timer
sudo systemctl enable --now fail2ban

# 6) Verify extractor and Fail2ban
sudo systemctl status pg-fail2ban-extract.timer | cat
sudo /usr/local/bin/postgres-docker-auth-extract.sh && sudo tail -n 5 /var/log/postgresql/postgres_auth_fail.log
sudo fail2ban-client reload
ls -l /var/run/fail2ban/fail2ban.sock
sudo fail2ban-client status
sudo fail2ban-client status postgresql
```

### How it works
- Docker logs remain JSON; the extractor pulls last ~minute, filters `FATAL:  password authentication failed for user ...`, appends to `/var/log/postgresql/postgres_auth_fail.log`.
- Fail2ban watches that file using the custom filter. Ban policy: `maxretry=5`, `findtime=600`, `bantime=3600`, port `5432`.

### Testing bans
```bash
# From another host ideally; otherwise remove 127.0.0.1 from ignore list in /etc/fail2ban/jail.local
for i in {1..6}; do PGPASSWORD=wrong psql -h 127.0.0.1 -p 5432 -U postgres -d mybot -c 'SELECT 1;' || true; done
# Trigger an immediate extraction run
sudo systemctl start pg-fail2ban-extract.service
# Check jail
sudo fail2ban-client status postgresql
```

### Notes
- The timer runs every 60s; extractor uses `--since 70s` to avoid gaps. Duplicate lines do not break Fail2ban.
- If you rotate `/var/log/postgresql/postgres_auth_fail.log`, reload Fail2ban after rotation.
- To unban: `sudo fail2ban-client set postgresql unbanip <IP>`