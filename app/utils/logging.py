"""
Enterprise Logging Configuration
Centralized logging setup with proper levels, formatting, and rotation
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from app.config.settings import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        """Format log record with colors for console output"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add colors to the formatter
        formatter = logging.Formatter(
            f"{log_color}%(asctime)s - %(name)s - %(levelname)s{reset_color} - %(message)s"
        )
        return formatter.format(record)


class BotLogger:
    """Enterprise logging manager for the bot application"""
    
    def __init__(self, name: str = "telegram_bot"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False
    
    def configure(self) -> logging.Logger:
        """Configure logging with enterprise settings"""
        if self._configured:
            return self.logger
            
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set logging level
        self.logger.setLevel(getattr(logging, config.logging.level.upper()))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # Create file handler if file path is specified
        if config.logging.file_path:
            self._setup_file_handler()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        self._configured = True
        return self.logger
    
    def _setup_file_handler(self) -> None:
        """Setup rotating file handler for logs"""
        log_file = Path(config.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=config.logging.max_file_size,
            backupCount=config.logging.backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(config.logging.format)
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
    
    def get_child_logger(self, name: str) -> logging.Logger:
        """Get a child logger for specific components"""
        return self.logger.getChild(name)


# Global logger instances
main_logger = BotLogger("telegram_bot")
logger = main_logger.configure()

# Component-specific loggers
auth_logger = main_logger.get_child_logger("auth")
payment_logger = main_logger.get_child_logger("payment")
product_logger = main_logger.get_child_logger("product")
crm_logger = main_logger.get_child_logger("crm")
lottery_logger = main_logger.get_child_logger("lottery")
cooperation_logger = main_logger.get_child_logger("cooperation")
database_logger = main_logger.get_child_logger("database")
notification_logger = main_logger.get_child_logger("notification")


def setup_telegram_logging():
    """Configure logging for python-telegram-bot library"""
    # Reduce telegram bot library logging verbosity
    telegram_logger = logging.getLogger("telegram")
    telegram_logger.setLevel(logging.WARNING)
    
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)


# Initialize telegram logging
setup_telegram_logging()


def log_function_call(func_name: str, user_id: Optional[int] = None, **kwargs):
    """Utility function to log function calls with context"""
    context_info = f"user_id={user_id}" if user_id else "system"
    if kwargs:
        context_info += f", {', '.join(f'{k}={v}' for k, v in kwargs.items())}"
    
    logger.debug(f"Function call: {func_name}({context_info})")


def log_error_with_context(error: Exception, context: str, user_id: Optional[int] = None, **kwargs):
    """Utility function to log errors with rich context"""
    context_info = f"user_id={user_id}" if user_id else "system"
    if kwargs:
        context_info += f", {', '.join(f'{k}={v}' for k, v in kwargs.items())}"
    
    logger.error(f"Error in {context}: {str(error)} | Context: {context_info}", exc_info=True)
