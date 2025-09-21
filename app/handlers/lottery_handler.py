"""
Lottery Handler
Lottery participation and management
"""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.services.database import BaseRepository, db_service
from app.models import Lottery, UsersInLottery
from app.constants.messages import LotteryMessages
from app.constants.conversation_states import ASK_LOTTERY, ASK_LOTTERY_NUMBER, ASK_LOTTERY_OTP
from app.utils.validation import InputValidator
from app.utils.logging import lottery_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import SMSException, LotteryException


class LotteryHandler:
    """Handler for lottery operations"""
    
    def __init__(self, sms_service: SMSService, notification_service: NotificationService):
        self.sms_service = sms_service
        self.notification_service = notification_service
        self.lottery_repository = BaseRepository(Lottery, db_service)
        self.users_in_lottery_repository = BaseRepository(UsersInLottery, db_service)
        self.logger = lottery_logger
    
    @handle_exceptions()
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start lottery conversation by showing available lotteries"""
        if not update.message:
            return ConversationHandler.END
        
        # Get active lotteries
        try:
            lotteries = await self.lottery_repository.find(is_active=True)
            
            if not lotteries:
                await update.message.reply_text(LotteryMessages.NO_LOTTERY_ACTIVE)
                return ConversationHandler.END
            
            # Create keyboard with lottery options
            keyboard = [[lottery.name] for lottery in lotteries]
            keyboard.append(["🔙 بازگشت به منو"])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            await update.message.reply_text(
                LotteryMessages.SELECT_LOTTERY,
                reply_markup=reply_markup
            )
            
            return ASK_LOTTERY
            
        except Exception as e:
            self.logger.error(f"Error showing lotteries: {str(e)}")
            await update.message.reply_text(LotteryMessages.NO_LOTTERY_ACTIVE)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle lottery selection"""
        if not update.message or not update.message.text:
            return ASK_LOTTERY
        
        lottery_name = update.message.text.strip()
        
        # Check if user wants to go back
        if lottery_name == "🔙 بازگشت به منو":
            # Clear user data and return to end conversation
            if context.user_data:
                context.user_data.clear()
            await update.message.reply_text("🔙 بازگشت به منوی اصلی...")
            return ConversationHandler.END
        
        try:
            # Get lottery by name
            lottery = await self.lottery_repository.get_by_field("name", lottery_name)
            
            if not lottery or not lottery.is_active:
                await update.message.reply_text(LotteryMessages.LOTTERY_NOT_FOUND)
                return ASK_LOTTERY
            
            # Store selected lottery in context
            if context.user_data is None:
                context.user_data = {}
            context.user_data["selected_lottery"] = lottery
            
            # Check if user is already registered for this lottery
            if update.effective_user:
                existing_user = await self.users_in_lottery_repository.get_by_field(
                    "telegram_id", update.effective_user.id
                )
                
                # Check if they're registered for THIS specific lottery
                if existing_user and existing_user.lottery_id == lottery.id:
                    await update.message.reply_text(
                        LotteryMessages.ALREADY_REGISTERED.format(lottery.name, lottery.description)
                    )
                    return ConversationHandler.END
            
            # Show lottery details and ask for phone number
            await update.message.reply_text(
                LotteryMessages.ASK_PHONE_LOTTERY.format(lottery.name, lottery.description),
                reply_markup=ReplyKeyboardRemove()
            )
            
            return ASK_LOTTERY_NUMBER
            
        except Exception as e:
            self.logger.error(f"Error handling lottery selection: {str(e)}")
            await update.message.reply_text(LotteryMessages.LOTTERY_NOT_FOUND)
            return ASK_LOTTERY
    
    @handle_exceptions()
    async def handle_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle phone number input for lottery"""
        if not update.message or not update.message.text:
            return ASK_LOTTERY_NUMBER
        
        phone = update.message.text.strip()
        is_valid, normalized_phone = InputValidator.validate_phone_number(phone)
        
        if not is_valid:
            await update.message.reply_text("❌ شماره وارد شده معتبر نیست. لطفاً شماره را به صورت صحیح وارد کنید:")
            return ASK_LOTTERY_NUMBER
        
        # Store phone in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["lottery_phone"] = normalized_phone
        
        # Generate and send OTP
        try:
            otp = self.sms_service.generate_otp()
            context.user_data["lottery_otp"] = otp
            
            await self.sms_service.send_otp(normalized_phone, otp)
            await update.message.reply_text(LotteryMessages.ASK_OTP_LOTTERY)
            
            self.logger.info(f"Lottery OTP sent to {normalized_phone}")
            return ASK_LOTTERY_OTP
            
        except SMSException as e:
            await update.message.reply_text(e.user_message)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle OTP verification and register user in lottery"""
        if not update.message or not update.message.text or not update.effective_user:
            return ASK_LOTTERY_OTP
        
        otp_input = update.message.text.strip()
        expected_otp = context.user_data.get("lottery_otp") if context.user_data else None
        
        if not expected_otp:
            await update.message.reply_text(LotteryMessages.INVALID_OTP_LOTTERY)
            return ASK_LOTTERY_OTP
        
        is_valid, _ = InputValidator.validate_otp(otp_input, expected_otp)
        
        if not is_valid:
            await update.message.reply_text(LotteryMessages.INVALID_OTP_LOTTERY)
            return ASK_LOTTERY_OTP
        
        # Register user in lottery
        try:
            phone = context.user_data["lottery_phone"]
            lottery = context.user_data["selected_lottery"]
            telegram_id = update.effective_user.id
            username = update.effective_user.username or ""
            
            # Double-check if user is already registered for this specific lottery
            existing_entries = await self.users_in_lottery_repository.find(
                telegram_id=telegram_id,
                lottery_id=lottery.id
            )
            
            if existing_entries:
                await update.message.reply_text(
                    f"✅ شما قبلاً در قرعه‌کشی '{lottery.name}' ثبت‌نام کرده‌اید!\n\nبازگشت به منو: /start"
                )
                return ConversationHandler.END
            
            # Create new lottery participation record
            await self.users_in_lottery_repository.create(
                telegram_id=telegram_id,
                username=username,
                number=phone,
                lottery_id=lottery.id,
                is_verified=True
            )
            
            # Send success message
            await update.message.reply_text(
                LotteryMessages.LOTTERY_SUCCESS.format(lottery.name, phone, lottery.name)
            )
            
            # Send notification to admin
            try:
                await self.notification_service.send_lottery_notification(
                    lottery_name=lottery.name,
                    telegram_id=telegram_id,
                    username=username,
                    phone=phone
                )
            except Exception as e:
                self.logger.error(f"Failed to send lottery notification: {str(e)}")
            
            # Clear user data
            if context.user_data:
                context.user_data.clear()
            
            self.logger.info(f"User {telegram_id} registered for lottery {lottery.name}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error registering user in lottery: {str(e)}")
            await update.message.reply_text("خطا در ثبت نام. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
