"""
Main Application Entry Point
Enterprise-level Telegram bot with proper architecture and dependency injection
"""

import asyncio
import signal
import sys
from typing import Optional

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

# Import configuration and services
from app.config.settings import config
from app.services.database import db_service
from app.services.user_service import user_service
from app.services.sms_service import sms_service
from app.services.notification_service import notification_service

# Import middleware and utilities
from app.middleware.error_handler import ErrorHandler
from app.utils.logging import logger, main_logger
from app.constants.conversation_states import *

# Import handlers
try:
    from app.handlers.registration_handler import RegistrationHandler
    from app.handlers.product_handler import ProductHandler
    from app.handlers.payment_handler import PaymentHandler
    from app.handlers.crm_handler import CRMHandler
    from app.handlers.lottery_handler import LotteryHandler
    from app.handlers.cooperation_handler import CooperationHandler
    from app.handlers.menu_handler import MenuHandler
except ImportError as e:
    logger.error(f"Failed to import handlers: {e}")
    raise ConfigurationException("handler_import", f"Handler import failed: {e}")

# Import exceptions
from app.exceptions.base import ConfigurationException


class TelegramBotApplication:
    """Main application class for the Telegram bot"""
    
    def __init__(self):
        self.application = None
        self.handlers = {}
        self._initialized = False
        self._shutdown_requested = False
    
    async def initialize(self) -> None:
        """Initialize the application and all services"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing Telegram Bot Application...")
            
            # Validate configuration
            config.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize database service
            db_service.initialize()
            await db_service.create_tables()
            logger.info("Database service initialized")
            
            # Initialize Telegram application
            self.application = ApplicationBuilder().token(config.telegram.bot_token).build()
            logger.info("Telegram application initialized")
            
            # Initialize handlers with dependency injection
            await self._initialize_handlers()
            
            # Setup conversation handlers
            self._setup_conversation_handlers()
            
            # Setup command and message handlers
            self._setup_basic_handlers()
            
            # Setup error handling
            self.application.add_error_handler(ErrorHandler.handle_error)
            
            self._initialized = True
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
            raise ConfigurationException(
                config_key="application_init",
                message=f"Application initialization failed: {str(e)}"
            )
    
    async def _initialize_handlers(self) -> None:
        """Initialize all conversation handlers with dependency injection"""
        
        # Initialize handlers with services
        self.handlers = {
            'registration': RegistrationHandler(user_service, sms_service, notification_service),
            'product': ProductHandler(user_service),
            'payment': PaymentHandler(user_service, notification_service),
            'crm': CRMHandler(sms_service, notification_service),
            'lottery': LotteryHandler(sms_service, notification_service),
            'cooperation': CooperationHandler(sms_service, notification_service),
        }
        
        # Initialize menu handler with reference to other handlers for proper dependency injection
        self.handlers['menu'] = MenuHandler(app_handlers=self.handlers)
        
        logger.info("Handlers initialized with dependency injection")
    
    def _setup_conversation_handlers(self) -> None:
        """Setup all conversation handlers"""
        
        # Main conversation handler (cooperation, lottery, menu navigation)
        main_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.handlers['menu'].start),
                MessageHandler(filters.Regex("^(🤝 همکاری با نمایندگی)$"), 
                               self.handlers['cooperation'].start_conversation),
                MessageHandler(filters.Regex("^(🎲 قرعه کشی)$"), 
                               self.handlers['lottery'].start_conversation)
            ],
            states={
                # Cooperation states
                ASK_COOPERATION_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                       self.handlers['cooperation'].handle_phone)],
                ASK_COOPERATION_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                     self.handlers['cooperation'].handle_otp)],
                ASK_COOPERATION_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                      self.handlers['cooperation'].handle_city)],
                ASK_COOPERATION_RESUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                        self.handlers['cooperation'].handle_resume)],
                
                # Lottery states
                ASK_LOTTERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                             self.handlers['lottery'].handle_selection)],
                ASK_LOTTERY_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                    self.handlers['lottery'].handle_phone)],
                ASK_LOTTERY_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                 self.handlers['lottery'].handle_otp)],
            },
            fallbacks=[
                CommandHandler("cancel", self.handlers['menu'].cancel),
                CommandHandler("start", self.handlers['menu'].start_and_end_conversation),
                MessageHandler(filters.Regex(
                    "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
                ), self.handlers['menu'].handle_menu_command_in_conversation)
            ],
            per_chat=True,
        )
        
        # Registration conversation handler
        registration_conversation = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^(👤 ثبت نام)$"), 
                               self.handlers['registration'].ask_name),
                CallbackQueryHandler(self.handlers['registration'].handle_authorize_callback, 
                                   pattern="^authorize$")
            ],
            states={
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                          self.handlers['registration'].handle_name)],
                ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                          self.handlers['registration'].handle_city)],
                ASK_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                          self.handlers['registration'].handle_area)],
                ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                        self.handlers['registration'].handle_id)],
                ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                           self.handlers['registration'].handle_phone)],
                ASK_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                         self.handlers['registration'].handle_otp)],
            },
            fallbacks=[
                CommandHandler("cancel", self.handlers['menu'].cancel),
                CommandHandler("start", self.handlers['menu'].start_and_end_conversation),
                MessageHandler(filters.Regex(
                    "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
                ), self.handlers['menu'].handle_menu_command_in_conversation)
            ],
        )
        
        # CRM conversation handler
        crm_conversation = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^(💬 مشاوره تلفنی رایگان)$"), 
                               self.handlers['crm'].ask_phone),
                CallbackQueryHandler(self.handlers['crm'].handle_not_sure_callback, 
                                   pattern="^not_sure$")
            ],
            states={
                ASK_CRM_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                               self.handlers['crm'].handle_phone)],
                ASK_CRM_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                             self.handlers['crm'].handle_otp)],
            },
            fallbacks=[
                CommandHandler("cancel", self.handlers['menu'].cancel),
                CommandHandler("start", self.handlers['menu'].start_and_end_conversation),
                MessageHandler(filters.Regex(
                    "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
                ), self.handlers['menu'].handle_menu_command_in_conversation)
            ],
            per_chat=True,
        )
        
        # Payment conversation handler
        payment_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.handlers['payment'].start_purchase, pattern="^buy_")
            ],
            states={
                ASK_REFERRAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                   self.handlers['payment'].handle_referral_code_input)],
                ASK_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                    self.handlers['payment'].handle_payment_method)],
                ASK_PAYMENT_PROOF: [MessageHandler(filters.PHOTO, 
                                                   self.handlers['payment'].handle_payment_proof)],
            },
            fallbacks=[
                CommandHandler("cancel", self.handlers['menu'].cancel),
                CommandHandler("start", self.handlers['menu'].start_and_end_conversation),
                MessageHandler(filters.Regex(
                    "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
                ), self.handlers['menu'].handle_menu_command_in_conversation)
            ],
        )
        
        # Receipt upload conversation handler
        receipt_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.handlers['payment'].handle_upload_receipt_callback, 
                                   pattern="^upload_receipt_")
            ],
            states={
                ASK_RECEIPT_INSTALLMENT: [
                    MessageHandler(filters.PHOTO, self.handlers['payment'].handle_receipt_upload)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.handlers['menu'].cancel),
                CommandHandler("start", self.handlers['menu'].start_and_end_conversation),
                MessageHandler(filters.Regex(
                    "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
                ), self.handlers['menu'].handle_menu_command_in_conversation)
            ],
            per_chat=True,
        )
        
        # Add all conversation handlers
        self.application.add_handler(main_conversation)
        self.application.add_handler(registration_conversation)
        self.application.add_handler(crm_conversation)
        self.application.add_handler(payment_conversation)
        self.application.add_handler(receipt_conversation)
        
        logger.info("Conversation handlers setup completed")
    
    def _setup_basic_handlers(self) -> None:
        """Setup basic command and message handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("help", self.handlers['menu'].help))
        self.application.add_handler(CommandHandler("products", self.handlers['product'].show_products_menu))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handlers['menu'].handle_button))
        
        # Message handlers
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, 
                           self.handlers['menu'].handle_reply_keyboard_button)
        )
        
        # Menu command handler (fallback)
        self.application.add_handler(
            MessageHandler(filters.Regex(
                "^(🔙 بازگشت به منو|👤 ثبت نام|🎲 قرعه کشی|📚 خرید ویژه محصولات از نمایندگی 📚|💡 راهنما|💬 تماس با ما|💎 خرید قسطی اشتراک الماس 💎|💳 اقساط من|💬 مشاوره تلفنی رایگان|👩‍💻 پشتیبانی|🤝 همکاری با نمایندگی)$"
            ), self.handlers['menu'].handle_menu_command_in_conversation)
        )
        
        logger.info("Basic handlers setup completed")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_requested = True
            
            # Create new event loop for cleanup if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.shutdown())
                else:
                    asyncio.run(self.shutdown())
            except RuntimeError:
                asyncio.run(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)
    
    async def run(self) -> None:
        """Run the bot application"""
        try:
            if not self._initialized:
                await self.initialize()
            
            self._setup_signal_handlers()
            
            logger.info("Starting Telegram bot...")
            logger.info(f"Bot configuration: {config.to_dict()}")
            
            # Start the bot
            await self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query', 'inline_query']
            )
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}", exc_info=True)
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the application"""
        logger.info("Shutting down application...")
        
        try:
            # Stop the telegram application
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram application stopped")
            
            # Close notification service
            await notification_service.close()
            logger.info("Notification service closed")
            
            # Close database service
            await db_service.close()
            logger.info("Database service closed")
            
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


async def main():
    """Main entry point"""
    app = TelegramBotApplication()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
