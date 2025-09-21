"""
Error Handling Middleware
Enterprise-level error handling with proper logging and user feedback
"""

import traceback
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from app.exceptions.base import (
    BotException, ValidationException, UserNotFoundException, 
    UserNotRegisteredException, ProductNotFoundException, 
    OrderNotFoundException, SMSException, DatabaseException
)
from app.utils.logging import logger, log_error_with_context
from app.constants.messages import ErrorMessages


class ErrorHandler:
    """Enterprise error handling middleware"""
    
    @staticmethod
    async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Global error handler for all bot operations
        """
        error = context.error
        
        # Extract user information if available
        user_id = None
        chat_id = None
        
        if isinstance(update, Update) and update.effective_user:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id if update.effective_chat else None
        
        # Log error with context
        log_error_with_context(
            error=error,
            context="telegram_bot_error",
            user_id=user_id,
            chat_id=chat_id,
            update_type=type(update).__name__ if update else "Unknown"
        )
        
        # Handle different types of exceptions
        await ErrorHandler._handle_specific_error(update, context, error, user_id, chat_id)
    
    @staticmethod
    async def _handle_specific_error(
        update: object,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        user_id: Optional[int],
        chat_id: Optional[int]
    ) -> None:
        """Handle specific exception types with appropriate user messages"""
        
        user_message = ErrorMessages.GENERAL_ERROR
        
        try:
            if isinstance(error, ValidationException):
                user_message = error.user_message
            elif isinstance(error, UserNotFoundException):
                user_message = error.user_message
            elif isinstance(error, UserNotRegisteredException):
                user_message = error.user_message
            elif isinstance(error, ProductNotFoundException):
                user_message = error.user_message
            elif isinstance(error, OrderNotFoundException):
                user_message = error.user_message
            elif isinstance(error, SMSException):
                user_message = error.user_message
            elif isinstance(error, DatabaseException):
                user_message = error.user_message
            elif isinstance(error, BotException):
                user_message = error.user_message
            else:
                # For unexpected errors, log full traceback
                logger.error(
                    f"Unexpected error for user {user_id}: {str(error)}",
                    exc_info=True
                )
                user_message = ErrorMessages.GENERAL_ERROR
            
            # Send user-friendly error message
            if isinstance(update, Update) and chat_id:
                await ErrorHandler._send_error_message(context, chat_id, user_message)
                
        except Exception as send_error:
            # If we can't even send an error message, log it
            logger.critical(
                f"Failed to send error message to user {user_id}: {str(send_error)}",
                exc_info=True
            )
    
    @staticmethod
    async def _send_error_message(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message: str
    ) -> None:
        """Send error message to user"""
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
        except Exception as e:
            logger.error(f"Failed to send error message to chat {chat_id}: {str(e)}")
    
    @staticmethod
    def log_and_raise(
        exception_class: type,
        message: str,
        context: str = "unknown",
        user_id: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Log error and raise custom exception
        """
        log_error_with_context(
            error=Exception(message),
            context=context,
            user_id=user_id,
            **kwargs
        )
        raise exception_class(message, **kwargs)


class ConversationErrorHandler:
    """Error handler specific to conversation flows"""
    
    @staticmethod
    def handle_validation_error(
        field_name: str,
        error_message: str,
        user_id: Optional[int] = None
    ) -> ValidationException:
        """Create and log validation error"""
        logger.warning(
            f"Validation error for field '{field_name}': {error_message}",
            extra={"user_id": user_id, "field": field_name}
        )
        return ValidationException(
            message=f"Validation failed for {field_name}: {error_message}",
            field_name=field_name,
            user_message=error_message
        )
    
    @staticmethod
    def handle_conversation_state_error(
        state: str,
        user_id: Optional[int] = None
    ) -> BotException:
        """Handle conversation state errors"""
        logger.error(
            f"Invalid conversation state: {state}",
            extra={"user_id": user_id, "state": state}
        )
        return BotException(
            message=f"Invalid conversation state: {state}",
            error_code="INVALID_CONVERSATION_STATE",
            user_message="خطا در وضعیت گفتگو. لطفا از منو شروع کنید: /start"
        )


# Decorator for function-level error handling
def handle_exceptions(
    default_message: str = ErrorMessages.GENERAL_ERROR,
    reraise: bool = False
):
    """
    Decorator for handling exceptions in handler functions
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BotException:
                # Re-raise bot exceptions as they're already handled
                if reraise:
                    raise
                logger.error(f"Bot exception in {func.__name__}", exc_info=True)
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                if reraise:
                    raise
                # Could send default message here if we have update/context
        return wrapper
    return decorator


# Global error handler instance
error_handler = ErrorHandler()
