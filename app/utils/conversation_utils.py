"""
Conversation Utilities
Helper functions for conversation management and cleanup
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from app.utils.logging import logger
from app.constants.messages import ErrorMessages


class ConversationUtils:
    """Utility class for conversation management"""
    
    @staticmethod
    def safe_cleanup_context(context: ContextTypes.DEFAULT_TYPE) -> None:
        """Safely clean up conversation context"""
        try:
            if context.user_data is not None:
                context.user_data.clear()
            logger.debug("Context cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up context: {str(e)}")
    
    @staticmethod
    async def handle_conversation_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error_message: str = None
    ) -> int:
        """Handle conversation errors and cleanup"""
        try:
            # Clean up context
            ConversationUtils.safe_cleanup_context(context)
            
            # Send error message
            if update.message:
                message = error_message or ErrorMessages.PROCESSING_ERROR
                await update.message.reply_text(
                    message,
                    reply_markup=ReplyKeyboardRemove()
                )
            elif update.callback_query:
                message = error_message or ErrorMessages.PROCESSING_ERROR  
                await update.callback_query.edit_message_text(message)
                
        except Exception as e:
            logger.error(f"Error in conversation error handler: {str(e)}")
        
        return ConversationHandler.END
    
    @staticmethod
    async def handle_user_cancellation(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        cancel_message: str = "عملیات لغو شد."
    ) -> int:
        """Handle user cancellation of conversation"""
        try:
            # Clean up context
            ConversationUtils.safe_cleanup_context(context)
            
            # Send cancellation message
            if update.message:
                await update.message.reply_text(
                    cancel_message,
                    reply_markup=ReplyKeyboardRemove()
                )
            
            logger.info(f"User {update.effective_user.id if update.effective_user else 'unknown'} cancelled conversation")
            
        except Exception as e:
            logger.error(f"Error handling user cancellation: {str(e)}")
        
        return ConversationHandler.END
    
    @staticmethod
    def safe_context_get(context: ContextTypes.DEFAULT_TYPE, key: str, default=None):
        """Safely get value from context user_data"""
        try:
            if context.user_data is None:
                return default
            return context.user_data.get(key, default)
        except Exception as e:
            logger.error(f"Error getting context key '{key}': {str(e)}")
            return default
    
    @staticmethod
    def safe_context_set(context: ContextTypes.DEFAULT_TYPE, key: str, value) -> bool:
        """Safely set value in context user_data"""
        try:
            if context.user_data is None:
                context.user_data = {}
            context.user_data[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting context key '{key}': {str(e)}")
            return False
