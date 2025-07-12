from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
import os
from dotenv import load_dotenv
from db import engine, Base, AsyncSessionLocal
import asyncio
from models import GradeEnum, MajorEnum, Product
from sqlalchemy import select

load_dotenv()

logging.basicConfig(level=logging.INFO)
# logging.info(f"[USER {update.effective_user.id}] sent: {user_input}")

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
}

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE, grade, major=None):
    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.grade == grade)
        if major:
            stmt = stmt.where(Product.major == major)
        result = await session.execute(stmt)
        products = result.scalars().all()
        if not products:
            await update.message.reply_text(f"محصولی برای این پایه و رشته یافت نشد")
            await products(update, context)
            return
        context.user_data["products"] = [p.name for p in products]
        keyboard = [[p.name] for p in products]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("برای دیدن جزییات و خرید روی محصول مورد نظر کلیک کنید:", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "authorize":
        await authorize(update, context)
    elif query.data == "lottery":
        await lottery(update, context)

async def handle_reply_keyboard_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    product_names = context.user_data.get("products",[])
    if user_input in product_names:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Product).where(Product.name == user_input))
            product = result.scalar_one_or_none()
            if product:
                await update.message.reply_text(f"جزییات محصول:\n{product.description}\nقیمت: {product.price}")
            else:
                await update.message.reply_text(f"محصول مورد نظر یافت نشد")
        return
    if user_input in grade_map:
        selected_grade = grade_map[user_input]
        context.user_data['grade'] = selected_grade
        if selected_grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12]:
            keyboard = [["ریاضی"], ["تجربی"], ["انسانی"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(f"برای انتخاب رشته مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
        else:
            await show_products(update, context, grade=selected_grade)
        return
    elif user_input in major_map:
        selected_major = major_map[user_input]
        grade = context.user_data.get('grade')
        if grade:
            await show_products(update, context, grade=grade, major=selected_major)
        else:
            await update.message.reply_text(f"لطفا پایه تحصیلی خود را انتخاب کنید.")
            await products(update, context)
        return
    elif user_input == "👤 ثبت نام":
        await authorize(update, context)
    elif user_input == "🎲 قرعه کشی":
        await lottery(update, context)
    elif user_input == "📚 محصولات":
        await products(update, context)
    elif user_input == "💡 راهنما":
        await help(update, context)
    elif user_input == "💬 تماس با ما":
        await contact(update, context)
    else:
        await update.message.reply_text(f"ببخشید نفهمیدم به چی نیاز داری! لطفا یکی از گزینه های منو رو انتخاب کنید.")
        await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user.id, update.effective_user.first_name, 
         update.effective_user.last_name, update.effective_user.username)
    keyboard = [
        ["👤 ثبت نام", "🎲 قرعه کشی"],
        ["📚 محصولات", "💡 راهنما"],
        ["💬 تماس با ما"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"سلام *{update.effective_user.first_name}!*به ربات ما خوش اومدی\nبرای استفاده از ربات گزینه مورد نظر رو انتخاب کنید.",
                                    parse_mode="Markdown", reply_markup=reply_markup)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"راهنما")

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(f"برای دیدن محصولات پایه تحصیلی مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)

async def lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"قرعه کشی")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"برای ارتباط با ما و پشتیبانی میتونید به آیدی @Arshya_Alaee پیام بدید😊")

async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"لطفا نام و نام خانوادگی خود را وارد کنید")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error: {context.error}")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    print(BOT_TOKEN)
    
    # Initialize database
    
    # Build and configure the application
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