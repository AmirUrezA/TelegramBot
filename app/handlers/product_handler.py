"""
Product Handler
Product browsing and selection
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from app.services.user_service import UserService
from app.services.database import BaseRepository, db_service
from app.models import Product
from app.constants.messages import ProductMessages
from app.utils.logging import product_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import ProductNotFoundException


class ProductHandler:
    """Handler for product-related operations"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.product_repository = BaseRepository(Product, db_service)
        self.logger = product_logger
    
    @handle_exceptions()
    async def show_products_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main products menu with grade selection"""
        if not update.message:
            return
        
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
        await update.message.reply_text(
            ProductMessages.GRADE_SELECTION,
            reply_markup=reply_markup
        )
        
        self.logger.info(f"Products menu shown to user {update.effective_user.id}")
    
    @handle_exceptions()
    async def show_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE, grade, major=None):
        """Show products for selected grade and major"""
        if not update.message:
            return
        
        try:
            # Get products from database
            filters = {"grade": grade}
            if major:
                filters["major"] = major
            
            products = await self.product_repository.find(**filters)
            
            if not products:
                await update.message.reply_text(ProductMessages.NO_PRODUCTS_FOUND)
                await self.show_products_menu(update, context)
                return
            
            # Store product names in context for later reference
            if context.user_data is None:
                context.user_data = {}
            context.user_data["products"] = [p.name for p in products]
            
            # Create keyboard with product names
            keyboard = [[p.name] for p in products]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            
            await update.message.reply_text(
                ProductMessages.PRODUCT_SELECTION,
                reply_markup=reply_markup
            )
            
            self.logger.info(f"Showed {len(products)} products for grade {grade.name}")
            
        except Exception as e:
            self.logger.error(f"Error showing products: {str(e)}")
            await update.message.reply_text(ProductMessages.NO_PRODUCTS_FOUND)
    
    @handle_exceptions()
    async def show_product_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, product_name: str):
        """Show details for a specific product"""
        if not update.message:
            return
        
        try:
            # Get product by name
            product = await self.product_repository.get_by_field("name", product_name)
            
            if not product:
                await update.message.reply_text(ProductMessages.PRODUCT_NOT_FOUND)
                return
            
            # Create inline keyboard with buy button
            keyboard = [
                [InlineKeyboardButton("🛒 خرید", callback_data=f"buy_{product.id}")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Format product details
            product_text = (
                f"جزییات محصول:\n{product.description}\n"
                f"قیمت: {product.formatted_price}"
            )
            
            await update.message.reply_text(
                product_text,
                reply_markup=reply_markup
            )
            
            self.logger.info(f"Product details shown: {product_name}")
            
        except Exception as e:
            self.logger.error(f"Error showing product details: {str(e)}")
            await update.message.reply_text(ProductMessages.PRODUCT_NOT_FOUND)
