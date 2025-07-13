from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
import os
from dotenv import load_dotenv
from db import engine, Base, AsyncSessionLocal
import asyncio
from models import GradeEnum, MajorEnum, Product, ReferralCode, User, Order, OrderStatusEnum
from sqlalchemy import select

load_dotenv()

logging.basicConfig(level=logging.INFO)

grade_map = {
    "پایه پنجم": GradeEnum.GRADE_5,
    "پایه ششم": GradeEnum.GRADE_6,
    "پایه هفتم": GradeEnum.GRADE_7,
    "پایه هشتم": GradeEnum.GRADE_8,
    "پایه نهم": GradeEnum.GRADE_9,
    "پایه دهم": GradeEnum.GRADE_10,
    "پایه یازدهم": GradeEnum.GRADE_11,
    "پایه دوازدهم": GradeEnum.GRADE_12,
}

major_map = {
    "ریاضی": MajorEnum.MATH,
    "تجربی": MajorEnum.SCIENCE,
    "انسانی": MajorEnum.LECTURE,
    "عمومی": MajorEnum.GENERAL,
}

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Start the buying process for a product"""
    print(f"buy_product called with product_id: {product_id}")  # Debug log
    
    if not update.effective_user:
        print("No effective_user")  # Debug log
        return
    async with AsyncSessionLocal() as session:
        user_id = update.effective_user.id
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        
        print(f"User found: {user is not None}, Approved: {user.approved if user else 'N/A'}")  # Debug log
        
        if not user or user.approved is False:
            keyboard = [
                [InlineKeyboardButton("👤 ثبت نام", callback_data="authorize")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "شما هنوز ثبت نام نکردید برای خرید نیاز است که ابتدا ثبت نام کنید", 
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    "شما هنوز ثبت نام نکردید برای خرید نیاز است که ابتدا ثبت نام کنید", 
                    reply_markup=reply_markup
                )
            return
        
        # Store product_id in context for later use
        if context.user_data is not None:
            context.user_data['current_product_id'] = product_id
        
        # Send referral code question
        keyboard = [
            ["کد معرف دارم"], 
            ["کد معرف ندارم(تخفیف پیشفرض ربات)"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        if update.callback_query:
            # For callback queries, send a new message
            await update.callback_query.message.reply_text("کد معرف دارید؟", reply_markup=reply_markup)
        else:
            await update.message.reply_text("کد معرف دارید؟", reply_markup=reply_markup)

async def handle_referral_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle referral code input from user"""
    if not update.message:
        return
    
    user_input = update.message.text
    
    if user_input == "کد معرف دارم":
        await update.message.reply_text("لطفا کد معرف خود را وارد کنید:")
        if context.user_data is not None:
            context.user_data['waiting_for_referral_code'] = True
        return
    elif user_input == "کد معرف ندارم(تخفیف پیشفرض ربات)":
        await process_order_without_referral(update, context)
        return
    elif context.user_data is not None and context.user_data.get('waiting_for_referral_code'):
        if user_input is not None:
            await process_order_with_referral(update, context, user_input)
        return

async def process_order_with_referral(update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str):
    """Process order with referral code"""
    if not update.effective_user or not update.message:
        return
    
    async with AsyncSessionLocal() as session:
        # Check if referral code exists and is valid
        referral_result = await session.execute(
            select(ReferralCode).where(ReferralCode.code == referral_code)
        )
        referral = referral_result.scalar_one_or_none()
        
        if not referral:
            await update.message.reply_text("کد معرف معتبر نیست. لطفا دوباره تلاش کنید:")
            return
        
        # Get product and user
        if context.user_data is None:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        product_id = context.user_data.get('current_product_id')
        if not product_id:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        
        product = await session.get(Product, product_id)
        user_result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        user = user_result.scalar_one_or_none()
        
        if not product or not user:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        
        # Calculate final price with discount
        discount_amount = referral.discount
        final_price = product.price - discount_amount
        
        # Create order
        order = Order(
            user_id=user.id,
            product_id=product.id,
            status=OrderStatusEnum.PENDING,
            referral_code_id=referral.id,
            discount_amount=discount_amount,
            final_price=final_price
        )
        
        session.add(order)
        await session.commit()
        
        # Clear context data
        if context.user_data is not None:
            context.user_data.pop('waiting_for_referral_code', None)
            context.user_data.pop('current_product_id', None)
        
        # Send confirmation message
        keyboard = [["🔙 بازگشت به منو"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = f"""✅ سفارش شما با موفقیت ثبت شد!

        📦 محصول: {product.name}
        💰 قیمت اصلی: {product.price:,} تومان
        🎫 کد معرف: {referral_code}
        💸 تخفیف: {referral.discount} تومان
        💵 قیمت نهایی: {final_price:,} تومان

        سفارش شما در حال بررسی است و به زودی با شما تماس خواهیم گرفت."""
        
        await update.message.reply_text(message, reply_markup=reply_markup)

async def process_order_without_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process order without referral code (default discount)"""
    if not update.effective_user or not update.message:
        return
    
    async with AsyncSessionLocal() as session:
        if context.user_data is None:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        product_id = context.user_data.get('current_product_id')
        if not product_id:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        
        product = await session.get(Product, product_id)
        user_result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        user = user_result.scalar_one_or_none()
        
        if not product or not user:
            await update.message.reply_text("خطا در پردازش سفارش. لطفا دوباره تلاش کنید.")
            return
        
        default_discount = 500000
        discount_amount = default_discount
        final_price = product.price - discount_amount
        
        order = Order(
            user_id=user.id,
            product_id=product.id,
            status=OrderStatusEnum.PENDING,
            discount_amount=default_discount,
            final_price=final_price
        )
        
        session.add(order)
        await session.commit()
        
        # Clear context data
        if context.user_data is not None:
            context.user_data.pop('waiting_for_referral_code', None)
            context.user_data.pop('current_product_id', None)
        
        # Send confirmation message
        keyboard = [["🔙 بازگشت به منو"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = f"""✅ سفارش شما با موفقیت ثبت شد!

        📦 محصول: {product.name}
        💰 قیمت اصلی: {product.price:,} تومان
        🎫 تخفیف پیشفرض: {default_discount} تومان
        💵 قیمت نهایی: {final_price:,} تومان

        سفارش شما در حال بررسی است و به زودی با شما تماس خواهیم گرفت."""
        
        await update.message.reply_text(message, reply_markup=reply_markup)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE, grade, major=None):
    """Show products for selected grade and major"""
    if not update.message:
        return
    
    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.grade == grade)
        if major:
            stmt = stmt.where(Product.major == major)
        result = await session.execute(stmt)
        products = result.scalars().all()
        
        if not products:
            await update.message.reply_text("محصولی برای این پایه و رشته یافت نشد")
            await show_products_menu(update, context)
            return
        
        if context.user_data is not None:
            context.user_data["products"] = [str(p.name) for p in products]
        keyboard = [[str(p.name)] for p in products]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(
            "برای دیدن جزییات و خرید روی محصول مورد نظر کلیک کنید:", 
            reply_markup=reply_markup
        )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    if not update.callback_query:
        return
    
    query = update.callback_query
    await query.answer()
    
    print(f"Button clicked: {query.data}")  # Debug log
    
    if query.data and query.data.startswith("buy_"):
        try:
            product_id = int(query.data.split("_")[1])
            print(f"Processing buy for product ID: {product_id}")  # Debug log
            
            # Call the buy_product function
            await buy_product(update, context, product_id)
            
        except (ValueError, IndexError) as e:
            print(f"Error parsing product ID: {e}")
            await query.edit_message_text("خطا در پردازش درخواست خرید")
    elif query.data == "back":
        await start(update, context)
    else:
        print(f"Unknown button data: {query.data}")  # Debug log

async def handle_reply_keyboard_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reply keyboard button presses"""
    if not update.message:
        return
    
    user_input = update.message.text
    if context.user_data is None:
        context.user_data = {}
    
    product_names = context.user_data.get("products", [])
    
    # Handle referral code flow
    if context.user_data.get('waiting_for_referral_code') or user_input in ["کد معرف دارم", "کد معرف ندارم(تخفیف پیشفرض ربات)"]:
        await handle_referral_code_input(update, context)
        return
    
    # Handle product selection
    if user_input in product_names:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Product).where(Product.name == user_input))
            product = result.scalar_one_or_none()
            if product:
                keyboard = [
                    [InlineKeyboardButton("🛒 خرید", callback_data=f"buy_{product.id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"جزییات محصول:\n{product.description}\nقیمت: {product.price:,} تومان", 
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("محصول مورد نظر یافت نشد")
        return
    
    # Handle grade selection
    elif user_input in grade_map:
        selected_grade = grade_map[user_input]
        context.user_data['grade'] = selected_grade
        if selected_grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12]:
            keyboard = [["ریاضی"], ["تجربی"], ["انسانی"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                "برای انتخاب رشته مورد نظر خود را انتخاب کنید:", 
                reply_markup=reply_markup
            )
        else:
            await show_products(update, context, grade=selected_grade)
        return
    
    # Handle major selection
    elif user_input in major_map:
        selected_major = major_map[user_input]
        grade = context.user_data.get('grade')
        if grade:
            await show_products(update, context, grade=grade, major=selected_major)
        else:
            await update.message.reply_text("لطفا پایه تحصیلی خود را انتخاب کنید.")
            await show_products_menu(update, context)
        return
    
    # Handle main menu options
    elif user_input == "👤 ثبت نام":
        await authorize(update, context)
    elif user_input == "🎲 قرعه کشی":
        await lottery(update, context)
    elif user_input == "📚 محصولات":
        await show_products_menu(update, context)
    elif user_input == "💡 راهنما":
        await help(update, context)
    elif user_input == "💬 تماس با ما":
        await contact(update, context)
    elif user_input == "🔙 بازگشت به منو":
        await start(update, context)
    else:
        await update.message.reply_text(
            "ببخشید نفهمیدم به چی نیاز داری! لطفا یکی از گزینه های منو رو انتخاب کنید."
        )
        await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    if not update.effective_user or not update.message:
        return
    
    print(update.effective_user.id, update.effective_user.first_name, 
         update.effective_user.last_name, update.effective_user.username)
    
    keyboard = [
        ["👤 ثبت نام", "🎲 قرعه کشی"],
        ["📚 محصولات", "💡 راهنما"],
        ["💬 تماس با ما"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        f"سلام *{update.effective_user.first_name}!* به ربات ما خوش اومدی\nبرای استفاده از ربات گزینه مورد نظر رو انتخاب کنید.",
        parse_mode="Markdown", 
        reply_markup=reply_markup
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    if not update.message:
        return
    
    help_text = """📚 راهنمای استفاده از ربات:

    🛒 نحوه خرید:
    1. روی "📚 محصولات" کلیک کنید
    2. پایه تحصیلی خود را انتخاب کنید
    3. برای پایه‌های دهم تا دوازدهم، رشته را انتخاب کنید
    4. محصول مورد نظر را انتخاب کنید
    5. روی "🛒 خرید" کلیک کنید
    6. کد معرف خود را وارد کنید (اختیاری)
    7. سفارش شما ثبت می‌شود

    🎫 کد معرف:
    • اگر کد معرف دارید: با وارد کردن کد معرف از تخفیف معرف بهره مند شوید
    • اگر کد معرف ندارید: میتونید از تخفیف پیشفرض ربات بهره مند شوید

    📞 پشتیبانی: @Arshya_Alaee"""
    
    await update.message.reply_text(help_text)

async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show products menu"""
    if not update.message:
        return
    
    keyboard = [
        ["پایه دوازدهم"],
        ["پایه یازدهم"],
        ["پایه دهم"],
        ["پایه نهم"],
        ["پایه هشتم"],
        ["پایه هفتم"],
        ["پایه ششم"],
        ["پایه پنجم"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "برای دیدن محصولات پایه تحصیلی مورد نظر خود را انتخاب کنید:", 
        reply_markup=reply_markup
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Products command handler"""
    await show_products_menu(update, context)

async def lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lottery command handler"""
    if not update.message:
        return
    
    await update.message.reply_text("🎲 قرعه کشی - به زودی فعال خواهد شد!")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact command handler"""
    if not update.message:
        return
    
    await update.message.reply_text(
        "برای ارتباط با ما و پشتیبانی میتونید به آیدی @Arshya_Alaee پیام بدید😊"
    )

async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Authorize command handler"""
    if not update.message:
        return
    
    await update.message.reply_text("لطفا نام و نام خانوادگی خود را وارد کنید")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logging.error(f"Update {update} caused error: {context.error}")

async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    app = ApplicationBuilder().token(str(BOT_TOKEN)).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("products", products))   
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_keyboard_button))
    app.add_error_handler(error_handler)
    
    print("Bot is running...")
    app.run_polling()
    asyncio.run(init_db())