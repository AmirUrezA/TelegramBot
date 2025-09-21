"""
Menu Handler
Main menu navigation and command handling
"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from app.constants.messages import WelcomeMessages, ContactMessages, ErrorMessages
from app.constants.mappings import MENU_COMMANDS, GRADE_MAP, MAJOR_MAP
from app.utils.logging import logger
from app.middleware.error_handler import handle_exceptions


class MenuHandler:
    """Handler for main menu and navigation"""
    
    def __init__(self, app_handlers=None):
        self.logger = logger.getChild('menu')
        self._app_handlers = app_handlers  # Reference to main app handlers
    
    @handle_exceptions()
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command and main menu"""
        if not update.effective_user or not update.message:
            return
        
        # Clear user data
        if context.user_data is not None:
            context.user_data.clear()
        
        # Handle deep links
        if context.args and len(context.args) > 0:
            command = context.args[0]
            if command == "cooperation" and self._app_handlers:
                return await self._app_handlers['cooperation'].start_conversation(update, context)
            elif command == "lottery" and self._app_handlers:
                return await self._app_handlers['lottery'].start_conversation(update, context)
        
        # Main menu keyboard
        keyboard = [
            ["💎 خرید قسطی اشتراک الماس 💎"],
            ["📚 خرید ویژه محصولات از نمایندگی 📚"],
            ["💰 درآمد زایی و معرفی دوستان", "💬 مشاوره تلفنی رایگان"],
            ["💳 اقساط من", "🎲 قرعه کشی"], 
            ["👩‍💻 پشتیبانی", "🤝 همکاری با نمایندگی"],
            ["👤 ثبت نام", "💡 راهنما"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            WelcomeMessages.MAIN_WELCOME,
            parse_mode="Markdown", 
            reply_markup=reply_markup
        )
        
        self.logger.info(f"Main menu shown to user {update.effective_user.id}")
    
    @handle_exceptions()
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle help command"""
        if not update.message:
            return
        
        await update.message.reply_text(ContactMessages.HELP_TEXT)
        self.logger.info(f"Help shown to user {update.effective_user.id}")
    
    @handle_exceptions()
    async def contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact command"""
        if not update.message:
            return
        
        await update.message.reply_text(ContactMessages.CONTACT_INFO)
        self.logger.info(f"Contact info shown to user {update.effective_user.id}")
    
    @handle_exceptions()
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle conversation cancellation"""
        from app.utils.conversation_utils import ConversationUtils
        
        # Use safe cleanup utility
        ConversationUtils.safe_cleanup_context(context)
        
        if update.message:
            await update.message.reply_text("عملیات لغو شد.")
            await self.start(update, context)
        return ConversationHandler.END
    
    @handle_exceptions()
    async def start_and_end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start menu and end current conversation"""
        await self.start(update, context)
        return ConversationHandler.END
    
    def is_menu_command(self, text: str) -> bool:
        """Check if text is a menu command"""
        return text in MENU_COMMANDS
    
    @handle_exceptions()
    async def handle_menu_command_in_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle menu commands during conversations"""
        if not update.message or not update.message.text:
            return ConversationHandler.END
        
        text = update.message.text.strip()
        
        # Clear conversation data
        if context.user_data is not None:
            context.user_data.clear()
        
        # Route to appropriate handler using proper dependency injection
        if text == "🔙 بازگشت به منو":
            await self.start(update, context)
        elif text == "👤 ثبت نام":
            if self._app_handlers and 'registration' in self._app_handlers:
                await self._app_handlers['registration'].ask_name(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        elif text == "🎲 قرعه کشی":
            if self._app_handlers and 'lottery' in self._app_handlers:
                await self._app_handlers['lottery'].start_conversation(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        elif text == "📚 خرید ویژه محصولات از نمایندگی 📚":
            if self._app_handlers and 'product' in self._app_handlers:
                await self._app_handlers['product'].show_products_menu(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        elif text == "💡 راهنما":
            await self.help(update, context)
        elif text == "💬 تماس با ما" or text == "👩‍💻 پشتیبانی":
            await self.contact(update, context)
        elif text == "💎 خرید قسطی اشتراک الماس 💎":
            await self._handle_almas_subscription(update, context)
        elif text == "💳 اقساط من":
            if self._app_handlers and 'payment' in self._app_handlers:
                await self._app_handlers['payment'].my_installments(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        elif text == "💬 مشاوره تلفنی رایگان":
            if self._app_handlers and 'crm' in self._app_handlers:
                await self._app_handlers['crm'].ask_phone(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        elif text == "🤝 همکاری با نمایندگی":
            if self._app_handlers and 'cooperation' in self._app_handlers:
                await self._app_handlers['cooperation'].start_conversation(update, context)
            else:
                await update.message.reply_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
                await self.start(update, context)
        else:
            await self.start(update, context)
        
        return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_reply_keyboard_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reply keyboard button presses"""
        if not update.message or not update.message.text:
            return
        
        user_input = update.message.text.strip()
        
        if context.user_data is None:
            context.user_data = {}
        
        # Check if this is a menu command
        if self.is_menu_command(user_input):
            if context.user_data is not None:
                context.user_data.clear()
            await self.handle_menu_command_in_conversation(update, context)
            return
        
        # Check if it's a grade selection
        if user_input in GRADE_MAP:
            await self._handle_grade_selection(update, context, user_input)
            return
        
        # Check if it's a major selection
        if user_input in MAJOR_MAP:
            await self._handle_major_selection(update, context, user_input)
            return
        
        # Check if it's a product name
        product_names = context.user_data.get("products", [])
        if user_input in product_names:
            await self._handle_product_selection(update, context, user_input)
            return
        
        # Default response
        await update.message.reply_text(ErrorMessages.GENERAL_ERROR)
        await self.start(update, context)
    
    async def _handle_almas_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Almas subscription selection"""
        keyboard = [
            ["پایه دوازدهم"],
            ["پایه یازدهم"],
            ["پایه دهم"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "💎اشتراک الماس رو فقط از طریق نمایندگی تهران میتونی اقساطی تهیه کنی‼️\n\n"
            "🎯دسترسی کامل به خدمات ماز تا روز کنکور \n"
            "💰پرداخت چند مرحله ای بدون بهره \n"
            "🎉دسترسی به خدمات تکمیلی نمایندگی\n\n"
            "🔻برای ادامه پایه تحصیلی خودتو انتخاب کن", 
            reply_markup=reply_markup
        )
    
    async def _handle_grade_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, grade_text: str):
        """Handle grade selection"""
        from app.handlers.product_handler import ProductHandler
        handler = ProductHandler(None)  # Will be properly injected
        
        selected_grade = GRADE_MAP[grade_text]
        context.user_data['grade'] = selected_grade
        
        # Check if major selection is needed
        from app.models.enums import GradeEnum
        if selected_grade in [GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12]:
            keyboard = [["ریاضی"], ["تجربی"], ["انسانی"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                "برای انتخاب رشته مورد نظر خود را انتخاب کنید:",
                reply_markup=reply_markup
            )
        else:
            await handler.show_products(update, context, grade=selected_grade)
    
    async def _handle_major_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, major_text: str):
        """Handle major selection"""
        from app.handlers.product_handler import ProductHandler
        handler = ProductHandler(None)  # Will be properly injected
        
        selected_major = MAJOR_MAP[major_text]
        grade = context.user_data.get('grade')
        
        if grade:
            await handler.show_products(update, context, grade=grade, major=selected_major)
        else:
            await update.message.reply_text("لطفا پایه تحصیلی خود را انتخاب کنید.")
            from app.handlers.product_handler import ProductHandler
            product_handler = ProductHandler(None)  # Will be properly injected
            await product_handler.show_products_menu(update, context)
    
    async def _handle_product_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, product_name: str):
        """Handle product selection"""
        from app.handlers.product_handler import ProductHandler
        handler = ProductHandler(None)  # Will be properly injected
        await handler.show_product_details(update, context, product_name)
    
    @handle_exceptions()
    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        if not update.callback_query:
            return
        
        query = update.callback_query
        await query.answer()
        
        self.logger.debug(f"Button clicked: {query.data}")
        
        if query.data == "back_to_menu":
            if context.user_data is not None:
                context.user_data.clear()
            
            await query.edit_message_text(
                WelcomeMessages.RETURN_TO_MENU,
                parse_mode="Markdown"
            )
        elif query.data == "authorize":
            await query.answer()
        elif query.data and query.data.startswith("my_installment_"):
            if self._app_handlers and 'payment' in self._app_handlers:
                await self._app_handlers['payment'].handle_my_installment(update, context)
            else:
                await query.edit_message_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
        elif query.data and query.data.startswith("installment_"):
            if self._app_handlers and 'payment' in self._app_handlers:
                await self._app_handlers['payment'].handle_single_installment(update, context)
            else:
                await query.edit_message_text("⚠️ خطا در سیستم. لطفا دوباره تلاش کنید.")
        elif query.data == "not_sure":
            await query.answer()
        else:
            self.logger.warning(f"Unknown button data: {query.data}")
