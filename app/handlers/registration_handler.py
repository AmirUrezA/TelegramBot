"""
Registration Handler
User registration and OTP verification
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from app.services.user_service import UserService
from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.constants.messages import RegistrationMessages
from app.constants.conversation_states import ASK_NAME, ASK_CITY, ASK_AREA, ASK_ID, ASK_PHONE, ASK_OTP
from app.utils.validation import InputValidator
from app.utils.logging import auth_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import ValidationException, SMSException


class RegistrationHandler:
    """Handler for user registration process"""
    
    def __init__(self, user_service: UserService, sms_service: SMSService, notification_service: NotificationService):
        self.user_service = user_service
        self.sms_service = sms_service
        self.notification_service = notification_service
        self.logger = auth_logger
    
    @handle_exceptions()
    async def ask_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start registration by asking for name"""
        if not update.message or not update.effective_user:
            return
        
        # Check if user is already registered
        if await self.user_service.is_user_registered(update.effective_user.id):
            await update.message.reply_text(RegistrationMessages.ALREADY_REGISTERED)
            return ConversationHandler.END
        
        await update.message.reply_text(RegistrationMessages.ASK_NAME)
        return ASK_NAME
    
    @handle_exceptions()
    async def handle_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle name input and move to city selection"""
        if not update.message or not update.message.text:
            return ASK_NAME
        
        name = update.message.text.strip()
        is_valid, normalized_name = InputValidator.validate_persian_name(name)
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_NAME)
            return ASK_NAME
        
        # Store in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["full_name"] = normalized_name
        
        await self._ask_city(update, context)
        return ASK_CITY
    
    async def _ask_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for city selection"""
        keyboard = [["تهران"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(RegistrationMessages.ASK_CITY, reply_markup=reply_markup)
    
    @handle_exceptions()
    async def handle_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle city selection and move to area"""
        if not update.message or not update.message.text:
            return ASK_CITY
        
        city = update.message.text.strip()
        is_valid, normalized_city = InputValidator.validate_city(city, ["تهران"])
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_CITY)
            return ASK_CITY
        
        # Store in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["city"] = normalized_city
        
        await update.message.reply_text(RegistrationMessages.ASK_AREA)
        return ASK_AREA
    
    @handle_exceptions()
    async def handle_area(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle area selection and move to national ID"""
        if not update.message or not update.message.text:
            return ASK_AREA
        
        area = update.message.text.strip()
        is_valid, normalized_area = InputValidator.validate_area_code(area)
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_AREA)
            return ASK_AREA
        
        # Store in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["area"] = normalized_area
        
        await update.message.reply_text(RegistrationMessages.ASK_ID)
        return ASK_ID
    
    @handle_exceptions()
    async def handle_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle national ID input and move to phone"""
        if not update.message or not update.message.text:
            return ASK_ID
        
        national_id = update.message.text.strip()
        is_valid, normalized_id = InputValidator.validate_national_id(national_id)
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_ID)
            return ASK_ID
        
        # Store in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["national_id"] = normalized_id
        
        await update.message.reply_text(RegistrationMessages.ASK_PHONE)
        return ASK_PHONE
    
    @handle_exceptions()
    async def handle_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle phone input and send OTP"""
        if not update.message or not update.message.text:
            return ASK_PHONE
        
        phone = update.message.text.strip()
        is_valid, normalized_phone = InputValidator.validate_phone_number(phone)
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_PHONE)
            return ASK_PHONE
        
        # Store phone number
        if context.user_data is None:
            context.user_data = {}
        context.user_data["phone"] = normalized_phone
        
        # Generate and send OTP
        try:
            otp = self.sms_service.generate_otp()
            context.user_data["otp"] = otp
            
            await self.sms_service.send_otp(normalized_phone, otp)
            await update.message.reply_text(RegistrationMessages.ASK_OTP)
            
            self.logger.info(f"OTP sent to {normalized_phone} for user {update.effective_user.id}")
            return ASK_OTP
            
        except SMSException as e:
            await update.message.reply_text(e.user_message)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle OTP verification and complete registration"""
        if not update.message or not update.message.text or not update.effective_user:
            return ASK_OTP
        
        otp_input = update.message.text.strip()
        expected_otp = context.user_data.get("otp") if context.user_data else None
        
        if not expected_otp:
            await update.message.reply_text(RegistrationMessages.INVALID_OTP)
            return ConversationHandler.END
        
        is_valid, normalized_otp = InputValidator.validate_otp(otp_input, expected_otp)
        
        if not is_valid:
            await update.message.reply_text(RegistrationMessages.INVALID_OTP)
            return ConversationHandler.END
        
        # Complete registration
        try:
            user = await self.user_service.complete_registration(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username or "",
                full_name=context.user_data["full_name"],
                city=context.user_data["city"],
                area=context.user_data["area"],
                national_id=context.user_data["national_id"],
                phone=context.user_data["phone"]
            )
            
            # Send success message
            await update.message.reply_text(RegistrationMessages.REGISTRATION_SUCCESS)
            
            # Send notification to admin
            try:
                await self.notification_service.send_registration_notification(
                    user_id=user.id,
                    telegram_id=user.telegram_id,
                    username=user.username,
                    full_name=user.full_name,
                    phone=user.number,
                    area=user.area
                )
            except Exception as e:
                self.logger.error(f"Failed to send registration notification: {str(e)}")
            
            # Show main menu
            from app.handlers.menu_handler import MenuHandler
            menu_handler = MenuHandler()
            await menu_handler.start(update, context)
            
            self.logger.info(f"User registration completed: {update.effective_user.id}")
            return ConversationHandler.END
            
        except ValidationException as e:
            await update.message.reply_text(e.user_message)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_authorize_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the authorize button click from inline keyboard"""
        if not update.callback_query:
            return ConversationHandler.END
        
        query = update.callback_query
        await query.answer()
        
        # Edit the message to remove the inline keyboard
        await query.edit_message_text("شروع فرآیند ثبت نام...")
        
        # Send the registration prompt
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=RegistrationMessages.ASK_NAME
        )
        
        return ASK_NAME
