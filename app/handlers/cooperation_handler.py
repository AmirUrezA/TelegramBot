"""
Cooperation Handler
Job application and cooperation request management
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.services.database import BaseRepository, db_service
from app.models import Cooperation
from app.constants.messages import CooperationMessages
from app.constants.conversation_states import ASK_COOPERATION_PHONE, ASK_COOPERATION_OTP, ASK_COOPERATION_CITY, ASK_COOPERATION_RESUME
from app.utils.validation import InputValidator
from app.utils.logging import cooperation_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import SMSException, CooperationException


class CooperationHandler:
    """Handler for cooperation application process"""
    
    def __init__(self, sms_service: SMSService, notification_service: NotificationService):
        self.sms_service = sms_service
        self.notification_service = notification_service
        self.cooperation_repository = BaseRepository(Cooperation, db_service)
        self.logger = cooperation_logger
    
    @handle_exceptions()
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start cooperation conversation by asking for phone number"""
        if not update.message:
            return ConversationHandler.END
        
        await update.message.reply_text(
            CooperationMessages.COOPERATION_INTRO,
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ASK_COOPERATION_PHONE
    
    @handle_exceptions()
    async def handle_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle phone number input and send OTP"""
        if not update.message or not update.message.text:
            return ASK_COOPERATION_PHONE
        
        phone = update.message.text.strip()
        is_valid, normalized_phone = InputValidator.validate_phone_number(phone)
        
        if not is_valid:
            await update.message.reply_text("❌ شماره وارد شده معتبر نیست. لطفاً شماره را به صورت صحیح وارد کنید:")
            return ASK_COOPERATION_PHONE
        
        # Store phone in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["cooperation_phone"] = normalized_phone
        
        # Generate and send OTP
        try:
            otp = self.sms_service.generate_otp()
            context.user_data["cooperation_otp"] = otp
            
            await self.sms_service.send_otp(normalized_phone, otp)
            await update.message.reply_text("✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:")
            
            self.logger.info(f"Cooperation OTP sent to {normalized_phone}")
            return ASK_COOPERATION_OTP
            
        except SMSException as e:
            await update.message.reply_text(e.user_message)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle OTP verification"""
        if not update.message or not update.message.text:
            return ASK_COOPERATION_OTP
        
        otp_input = update.message.text.strip()
        expected_otp = context.user_data.get("cooperation_otp") if context.user_data else None
        
        if not expected_otp:
            await update.message.reply_text("❌ کد وارد شده صحیح نیست. لطفا دوباره تلاش کنید:")
            return ASK_COOPERATION_OTP
        
        is_valid, _ = InputValidator.validate_otp(otp_input, expected_otp)
        
        if not is_valid:
            await update.message.reply_text("❌ کد وارد شده صحیح نیست. لطفا دوباره تلاش کنید:")
            return ASK_COOPERATION_OTP
        
        await update.message.reply_text(CooperationMessages.ASK_OTP_COOPERATION)
        return ASK_COOPERATION_CITY
    
    @handle_exceptions()
    async def handle_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle city input"""
        if not update.message or not update.message.text:
            return ASK_COOPERATION_CITY
        
        city = update.message.text.strip()
        is_valid, normalized_city = InputValidator.validate_city(city)
        
        if not is_valid:
            await update.message.reply_text(CooperationMessages.ASK_CITY_COOPERATION)
            return ASK_COOPERATION_CITY
        
        # Store city in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["cooperation_city"] = normalized_city
        
        await update.message.reply_text(
            f"{CooperationMessages.CITY_REGISTERED}\n\n{CooperationMessages.ASK_RESUME}"
        )
        
        return ASK_COOPERATION_RESUME
    
    @handle_exceptions()
    async def handle_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle resume text and save to database"""
        if not update.message or not update.effective_user:
            return ASK_COOPERATION_RESUME
        
        # Check if user sent text (not file or photo)
        if not update.message.text:
            if update.message.document or update.message.photo:
                await update.message.reply_text(CooperationMessages.TEXT_ONLY_RESUME)
                return ASK_COOPERATION_RESUME
            return ASK_COOPERATION_RESUME
        
        resume_text = update.message.text.strip()
        is_valid, normalized_resume = InputValidator.validate_resume_text(resume_text, min_length=50)
        
        if not is_valid:
            await update.message.reply_text(CooperationMessages.RESUME_TOO_SHORT)
            return ASK_COOPERATION_RESUME
        
        # Get stored data with safety checks
        from app.utils.conversation_utils import ConversationUtils
        
        if not context.user_data:
            await ConversationUtils.handle_conversation_error(
                update, context, "خطا در اطلاعات. لطفا دوباره شروع کنید: /start"
            )
            return ConversationHandler.END
            
        phone = ConversationUtils.safe_context_get(context, "cooperation_phone")
        city = ConversationUtils.safe_context_get(context, "cooperation_city")
        telegram_id = update.effective_user.id
        username = update.effective_user.username or ""
        
        if not phone or not city:
            await ConversationUtils.handle_conversation_error(
                update, context, "خطا در اطلاعات. لطفا دوباره شروع کنید: /start"
            )
            return ConversationHandler.END
        
        # Save to database
        try:
            # Check if user already submitted cooperation application
            existing_cooperation = await self.cooperation_repository.get_by_field(
                "telegram_id", telegram_id
            )
            
            if existing_cooperation:
                # Update existing record
                await self.cooperation_repository.update(
                    existing_cooperation.id,
                    phone_number=phone,
                    city=city,
                    resume_text=normalized_resume,
                    username=username,
                    status="pending"  # Reset status for new application
                )
                
                await update.message.reply_text(CooperationMessages.COOPERATION_UPDATE_SUCCESS)
            else:
                # Create new record
                await self.cooperation_repository.create(
                    telegram_id=telegram_id,
                    username=username,
                    phone_number=phone,
                    city=city,
                    resume_text=normalized_resume,
                    status="pending"
                )
                
                await update.message.reply_text(CooperationMessages.COOPERATION_SUCCESS)
            
            # Send notification to admin
            try:
                await self.notification_service.send_cooperation_notification(
                    telegram_id=telegram_id,
                    username=username,
                    phone=phone,
                    city=city,
                    resume_text=normalized_resume
                )
            except Exception as e:
                self.logger.error(f"Failed to send cooperation notification: {str(e)}")
            
            # Clear user data
            if context.user_data:
                context.user_data.clear()
            
            self.logger.info(f"Cooperation application saved for user {telegram_id}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error saving cooperation application: {str(e)}")
            await update.message.reply_text("خطا در ثبت درخواست. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
