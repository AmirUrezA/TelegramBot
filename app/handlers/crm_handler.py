"""
CRM Handler
Customer consultation requests and phone verification
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.services.database import BaseRepository, db_service
from app.models import CRM
from app.constants.messages import CRMMessages
from app.constants.conversation_states import ASK_CRM_PHONE, ASK_CRM_OTP
from app.utils.validation import InputValidator
from app.utils.logging import crm_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import SMSException


class CRMHandler:
    """Handler for CRM consultation requests"""
    
    def __init__(self, sms_service: SMSService, notification_service: NotificationService):
        self.sms_service = sms_service
        self.notification_service = notification_service
        self.crm_repository = BaseRepository(CRM, db_service)
        self.logger = crm_logger
    
    @handle_exceptions()
    async def ask_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start CRM process by asking for phone number"""
        if not update.message:
            return ConversationHandler.END
        
        await update.message.reply_text(CRMMessages.ASK_PHONE)
        return ASK_CRM_PHONE
    
    @handle_exceptions()
    async def handle_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle phone number input and send OTP"""
        if not update.message or not update.message.text:
            return ASK_CRM_PHONE
        
        phone = update.message.text.strip()
        is_valid, normalized_phone = InputValidator.validate_phone_number(phone)
        
        if not is_valid:
            await update.message.reply_text(CRMMessages.ASK_PHONE)
            return ASK_CRM_PHONE
        
        # Store phone in context
        if context.user_data is None:
            context.user_data = {}
        context.user_data["crm_phone"] = normalized_phone
        
        # Generate and send OTP
        try:
            otp = self.sms_service.generate_otp()
            context.user_data["crm_otp"] = otp
            
            await self.sms_service.send_otp(normalized_phone, otp)
            await update.message.reply_text(CRMMessages.ASK_OTP_CRM)
            
            self.logger.info(f"CRM OTP sent to {normalized_phone}")
            return ASK_CRM_OTP
            
        except SMSException as e:
            await update.message.reply_text(e.user_message)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle OTP verification and save CRM request"""
        if not update.message or not update.message.text or not update.effective_user:
            return ASK_CRM_OTP
        
        otp_input = update.message.text.strip()
        expected_otp = context.user_data.get("crm_otp") if context.user_data else None
        
        if not expected_otp:
            await update.message.reply_text(CRMMessages.INVALID_OTP_CRM)
            return ASK_CRM_OTP
        
        is_valid, _ = InputValidator.validate_otp(otp_input, expected_otp)
        
        if not is_valid:
            await update.message.reply_text(CRMMessages.INVALID_OTP_CRM)
            return ASK_CRM_OTP
        
        # Save CRM request
        try:
            phone = context.user_data["crm_phone"]
            
            # Check if this phone number already exists
            existing_crm = await self.crm_repository.get_by_field("number", phone)
            
            if existing_crm:
                # Update existing record
                await self.crm_repository.update(
                    existing_crm.id,
                    called=False,  # Reset called status for new request
                    notes=None,
                    priority=1
                )
            else:
                # Create new CRM record
                await self.crm_repository.create(
                    number=phone,
                    called=False,
                    priority=1
                )
            
            # Send success message
            await update.message.reply_text(CRMMessages.CRM_SUCCESS)
            
            # Send notification to admin
            try:
                await self.notification_service.send_crm_notification(
                    phone=phone,
                    telegram_id=update.effective_user.id,
                    username=update.effective_user.username or ""
                )
            except Exception as e:
                self.logger.error(f"Failed to send CRM notification: {str(e)}")
            
            self.logger.info(f"CRM request saved for phone {phone}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error saving CRM request: {str(e)}")
            await update.message.reply_text("خطا در ثبت درخواست. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_not_sure_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle 'not sure' button callback"""
        if not update.callback_query:
            return ConversationHandler.END
        
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(CRMMessages.NOT_SURE_GUIDANCE)
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=CRMMessages.ASK_PHONE
        )
        
        return ASK_CRM_PHONE
