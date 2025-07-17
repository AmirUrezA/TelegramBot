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
