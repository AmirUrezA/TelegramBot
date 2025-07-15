from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
import logging
import os
from dotenv import load_dotenv
from db import engine, Base, AsyncSessionLocal
import asyncio
from models import GradeEnum, MajorEnum, Product, ReferralCode, User, Order, OrderStatusEnum, ReferralCodeProductEnum, File, CRM
from sqlalchemy import select, insert
from kavenegar import *
import re
import random
from typing import Optional
from datetime import datetime

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

(ASK_NAME, ASK_PHONE, ASK_OTP) = range(3)

ASK_PAYMENT_METHOD, ASK_PAYMENT_PROOF = range(100, 102)

# Card number (static)
CARD_NUMBER = "6037-9918-6186-2085"

def is_valid_persian_name(name: str) -> bool:
    # فقط حروف فارسی، بین 2 تا 5 کلمه
    return bool(re.fullmatch(r"[آ-ی\s]{5,50}", name.strip()))

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    async with AsyncSessionLocal() as session:
        telegram_id = update.effective_user.id
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user and user.approved is True:
            await update.message.reply_text("شما قبلاً ثبت‌نام کردید ✅")
            return ConversationHandler.END
    await update.message.reply_text("👤 لطفاً نام و نام خانوادگی خود را به فارسی وارد کنید:")
    return ASK_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    name = update.message.text.strip()
    if not is_valid_persian_name(name):
        await update.message.reply_text("❌ لطفاً نام و نام خانوادگی را به‌درستی و به زبان فارسی وارد کنید.")
        return ASK_NAME
    
    if context.user_data is None:
        context.user_data = {}
    context.user_data["full_name"] = name
    await update.message.reply_text("📱 حالا شماره موبایل خود را وارد کنید (مثال: 09123456789):")
    return ASK_PHONE

def is_valid_phone(number: str) -> bool:
    return bool(re.fullmatch(r"09\d{9}", number))

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    phone = update.message.text.strip()
    if not is_valid_phone(phone):
        await update.message.reply_text("❌ شماره وارد شده معتبر نیست. لطفاً شماره را به صورت صحیح وارد کنید.")
        return ASK_PHONE

    if context.user_data is None:
        context.user_data = {}
    context.user_data["phone"] = phone

    otp = str(random.randint(1000, 9999))
    context.user_data["otp"] = otp

    # ارسال OTP با Kavenegar
    try:
        api = KavenegarAPI(os.getenv("KAVENEGAR_API_KEY"))
        api.verify_lookup({
            "receptor": phone,
            "token": otp,
            "template": "verify",
            "type": "sms"
        })
    except Exception as e:
        await update.message.reply_text(f"خطا در ارسال پیامک: {e}")
        return ConversationHandler.END

    await update.message.reply_text("✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:")
    return ASK_OTP

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo or not update.effective_user:
        await update.message.reply_text("لطفاً یک عکس از فیش واریزی ارسال کنید.")
        return ASK_PAYMENT_PROOF

    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Download the photo to local storage
    bot = context.bot
    file = await bot.get_file(file_id)
    file_path = f"receipts/receipt_{file_id}.jpg"
    os.makedirs("receipts", exist_ok=True)
    await file.download_to_drive(file_path)

    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == update.effective_user.id))
        user = user_result.scalar_one_or_none()
        if not user:
            await update.message.reply_text("کاربر یافت نشد.")
            return ConversationHandler.END

        product = context.user_data.get("product_data")
        referral = context.user_data.get("referral_data")
        final_price = context.user_data.get("final_price")
        installment = context.user_data.get("payment_type") == 'installment'
        first_installment_amount = context.user_data.get("first_installment")

        file_record = File(file_id=file_id, path=file_path)
        session.add(file_record)
        await session.flush()  # Get file.id before commit

        order = Order(
            user_id=user.id,
            product_id=product.id,
            status=OrderStatusEnum.PENDING,
            discount=referral.discount if referral else context.user_data.get("discount", 0),
            final_price=final_price,
            installment=installment,
            first_installment=datetime.now() if installment else None
        )

        session.add(order)
        await session.flush()  # Get order.id before commit

        await session.execute(insert(Order.__table__.metadata.tables['order_receipts']).values(order_id=order.id, file_id=file_record.id))
        await session.commit()

    await update.message.reply_text("✅ سفارش شما ثبت شد. بسته شما تا ساعاتی دیگر ارسال خواهد شد.")
    return ConversationHandler.END

async def handle_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user:
        return
    code = update.message.text.strip()
    if context.user_data is None or code != context.user_data.get("otp"):
        await update.message.reply_text("❌ کد وارد شده صحیح نیست. دوباره تلاش کنید:")
        return ASK_OTP

    full_name = context.user_data["full_name"]
    phone = context.user_data["phone"]
    telegram_id = update.effective_user.id
    username = update.effective_user.username or ""

    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_result.scalar_one_or_none()

        if user:
            # Use setattr to avoid type checking issues
            setattr(user, 'approved', True)
            setattr(user, 'number', phone)
            setattr(user, 'username', username)
        else:
            user = User(
                telegram_id=telegram_id,
                username=username,
                number=phone,
                approved=True
            )
            session.add(user)

        await session.commit()

    await update.message.reply_text("🎉 ثبت‌نام شما با موفقیت انجام شد!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("ثبت‌نام لغو شد.")
    return ConversationHandler.END

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
                [InlineKeyboardButton("هنوز مطمعن نیستم", callback_data="not_sure")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "شما هنوز ثبت نام نکردید برای خرید نیاز است که ابتدا ثبت نام کنید", 
                    reply_markup=reply_markup
                )
            elif update.message:
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
            await update.callback_query.answer()
            # Use context to send a new message
            await context.bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text="کد معرف دارید؟",
                reply_markup=reply_markup
            )
        elif update.message:
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
        context.user_data['waiting_for_referral_code'] = False
        await process_order_without_referral(update, context)
        return
    elif context.user_data is not None and context.user_data.get('waiting_for_referral_code'):
        if user_input is not None:
            await process_order_with_referral(update, context, user_input)
        return

async def process_order_with_referral(update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str):
    if not update.effective_user or not update.message:
        return

    async with AsyncSessionLocal() as session:
        referral_result = await session.execute(
            select(ReferralCode).where(ReferralCode.code == referral_code)
        )
        referral = referral_result.scalar_one_or_none()

        if not referral:
            await update.message.reply_text("کد معرف معتبر نیست. لطفا دوباره تلاش کنید:")
            return

        if context.user_data is None:
            context.user_data = {}

        context.user_data['referral'] = referral_code
        context.user_data['referral_data'] = referral
        context.user_data['waiting_for_referral_code'] = False

        product_id = context.user_data.get('current_product_id')
        product = await session.get(Product, product_id)
        context.user_data['product_data'] = product

        # Check if user can choose installment
        if product.grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12] and referral.product == ReferralCodeProductEnum.ALMAS and referral.installment:
            keyboard = ReplyKeyboardMarkup([
                ["پرداخت قسطی"],
                ["پرداخت نقدی"]
            ], resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("نوع پرداخت خود را انتخاب کنید:", reply_markup=keyboard)
            return ASK_PAYMENT_METHOD
        elif product.grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12] and referral.product == ReferralCodeProductEnum.ALMAS and not referral.installment:
            keyboard = ReplyKeyboardMarkup([
                ["پرداخت نقدی"],
                ["🔙 بازگشت به منو"]
            ], resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("کد تخفیف شما قابلیت پرداخت قسطی ندارد میتوانید از شرایط اقساطی پیشفرض ربات استفاده کنید و پرداخت قسطی انجام دهید برای این کار دکمه بازگشت را بفرستید در غیر این صورت خرید نقدی را انتخاب کنید:", reply_markup=keyboard)
            await ask_for_payment_proof(update, context)
            return ASK_PAYMENT_PROOF
        else:
            context.user_data['payment_type'] = 'cash'
            await ask_for_payment_proof(update, context)
            return ASK_PAYMENT_PROOF

async def process_order_without_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    async with AsyncSessionLocal() as session:
        if context.user_data is None:
            context.user_data = {}

        product_id = context.user_data.get('current_product_id')
        product = await session.get(Product, product_id)
        context.user_data['product_data'] = product

        context.user_data['referral'] = None
        context.user_data['discount'] = 500000
        context.user_data['waiting_for_referral_code'] = False


        # Check if installment is allowed
        if product.grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12]:
            keyboard = ReplyKeyboardMarkup([
                ["پرداخت قسطی"],
                ["پرداخت نقدی"]
            ], resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("نوع پرداخت خود را انتخاب کنید:", reply_markup=keyboard)
            return ASK_PAYMENT_METHOD
        else:
            context.user_data['payment_type'] = 'cash'
            await ask_for_payment_proof(update, context)
            return ASK_PAYMENT_PROOF

async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    payment_type = update.message.text.strip()
    if context.user_data is None:
        context.user_data = {}

    if payment_type not in ["پرداخت نقدی", "پرداخت قسطی"]:
        await update.message.reply_text("❌ لطفا یکی از گزینه‌های پرداخت را انتخاب کنید.")
        return ASK_PAYMENT_METHOD

    context.user_data['payment_type'] = 'installment' if payment_type == "پرداخت قسطی" else 'cash'
    await ask_for_payment_proof(update, context)
    return ASK_PAYMENT_PROOF

async def ask_for_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    product = context.user_data.get("product_data")
    discount = 0
    referral = context.user_data.get("referral_data")

    if referral:
        discount = referral.discount
    else:
        discount = context.user_data.get("discount", 0)

    final_price = product.price - discount
    installment = context.user_data['payment_type'] == 'installment'

    if installment:
        first_payment = final_price // 3
        msg = f"💳 مبلغ قسط اول: {first_payment:,} تومان\nشماره کارت برای واریز: {CARD_NUMBER}\n\n📸 لطفا اسکرین‌شات رسید واریزی را ارسال کنید."
    else:
        msg = f"💳 مبلغ قابل پرداخت: {final_price:,} تومان\nشماره کارت برای واریز: {CARD_NUMBER}\n\n📸 لطفا اسکرین‌شات رسید واریزی را ارسال کنید."

    context.user_data['final_price'] = final_price
    context.user_data['first_installment'] = final_price // 3 if installment else final_price

    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ASK_PAYMENT_PROOF

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
    elif query.data == "back_to_menu":
        await start(update, context)
    elif query.data == "authorize":
        return await ask_name(update, context)
    else:
        print(f"Unknown button data: {query.data}")  # Debug log

async def handle_crm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    phone = update.message.text.strip()
    if not is_valid_phone(phone):
        await update.message.reply_text("❌ شماره وارد شده معتبر نیست. لطفاً شماره را به صورت صحیح وارد کنید.")
        return ASK_PHONE

    if context.user_data is None:
        context.user_data = {}
    context.user_data["phone"] = phone

    otp = str(random.randint(1000, 9999))
    context.user_data["otp"] = otp

    # ارسال OTP با Kavenegar
    try:
        api = KavenegarAPI(os.getenv("KAVENEGAR_API_KEY"))
        api.verify_lookup({
            "receptor": phone,
            "token": otp,
            "template": "verify",
            "type": "sms"
        })
    except Exception as e:
        await update.message.reply_text(f"خطا در ارسال پیامک: {e}")
        return ConversationHandler.END

    await update.message.reply_text("✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:")
    return ASK_OTP
    

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
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu")]
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
        return await ask_name(update, context)
    elif user_input == "🎲 قرعه کشی":
        await lottery(update, context)
    elif user_input == "📚 خرید محصولات با تخفیف ویژه نمایندگی 📚":
        await show_products_menu(update, context)
    elif user_input == "💡 راهنما":
        await help(update, context)
    elif user_input == "💬 تماس با ما":
        await contact(update, context)
    elif user_input == "🔙 بازگشت به منو":
        await start(update, context)
    elif user_input == "💎 خرید قسطی اشتراک الماس 💎":
        keyboard = [
            ["پایه دوازدهم"],
            ["پایه یازدهم"],
            ["پایه دهم"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "💎اشتراک الماس رو فقط از طریق نمایندگی تهران میتونی اقساطی تهیه کنی‼️\n\n🎯دسترسی کامل به خدمات ماز تا روز کنکور \n💰پرداخت چند مرحله ای بدون بهره \n🎉دسترسی به خدمات تکمیلی نمایندگی\n\n🔻برای ادامه پایه تحصیلی خودتو انتخاب کن", 
            reply_markup=reply_markup
        )
    elif user_input == "💬 مشاوره تلفنی رایگان":
        print("crm")
        await handle_crm(update, context)
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
        ["💎 خرید قسطی اشتراک الماس 💎"],
        ["📚 خرید محصولات با تخفیف ویژه نمایندگی 📚"],
        ["💰 درآمد زایی و معرفی دوستان", "💬 مشاوره تلفنی رایگان"],
        ["💳 اقساط من", "🎲 قرعه کشی"], 
        ["👩‍💻 پشتیبانی", "🤝 همکاری با نمایندگی"],
        ["👤 ثبت نام", "💡 راهنما"]

    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        f"سلام دوست خوبم👋\n🤖به ربات ماز خوش اومدی🤖\n\nمن اینجام تا مرحله به مرحله در خصوص تخفیف ها ، مشاوره و شرایط اقساطی نمایندگی ماز راهنماییت کنم🦾\n\n🔻از منوی زیر بخش مورد نظرت رو انتخاب کن تا به امکانات من دسترسی داشته باشی😉",
  
        parse_mode="Markdown", 
        reply_markup=reply_markup
    )
    context.user_data = {}

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
    
    app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(👤 ثبت نام)$"), ask_name)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
        ASK_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    ))
    app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(🛒 خرید)$"), buy_product)],
    states={
        ASK_PAYMENT_METHOD: [MessageHandler(filters.TEXT, handle_payment_method)],
        ASK_PAYMENT_PROOF: [MessageHandler(filters.PHOTO, handle_payment_proof)],
    },    
    fallbacks=[CommandHandler("cancel", cancel)],
    ))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("products", products))   
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.Regex("^(پرداخت نقدی|پرداخت قسطی)$"), handle_payment_method))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_keyboard_button))
    app.add_error_handler(error_handler)

    
    print("Bot is running...")
    app.run_polling()
    asyncio.run(init_db())