"""
Payment Handler
Purchase process, installments, and receipt management
"""

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.services.database import BaseRepository, db_service
from app.models import Product, ReferralCode, Order, File
from app.models.enums import GradeEnum, OrderStatusEnum, ReferralCodeProductEnum
from app.constants.messages import ProductMessages, PaymentMessages, InstallmentMessages, ErrorMessages
from app.constants.conversation_states import ASK_REFERRAL_CODE, ASK_PAYMENT_METHOD, ASK_PAYMENT_PROOF, ASK_RECEIPT_INSTALLMENT
from app.constants.mappings import HIGH_SCHOOL_GRADES
from app.config.settings import config
from app.utils.logging import payment_logger
from app.middleware.error_handler import handle_exceptions
from app.exceptions.base import UserNotRegisteredException, ProductNotFoundException, ValidationException


class PaymentHandler:
    """Handler for payment and purchase operations"""
    
    def __init__(self, user_service: UserService, notification_service: NotificationService):
        self.user_service = user_service
        self.notification_service = notification_service
        self.product_repository = BaseRepository(Product, db_service)
        self.referral_repository = BaseRepository(ReferralCode, db_service)
        self.order_repository = BaseRepository(Order, db_service)
        self.file_repository = BaseRepository(File, db_service)
        self.logger = payment_logger
    
    @handle_exceptions()
    async def start_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the purchase process for a product"""
        if not update.callback_query or not update.effective_user:
            return
        
        query = update.callback_query
        await query.answer()
        
        # Extract product ID from callback data
        try:
            product_id = int(query.data.split("_")[1])
        except (IndexError, ValueError):
            await query.edit_message_text("خطا در شناسایی محصول")
            return ConversationHandler.END
        
        # Check if user is registered
        try:
            user = await self.user_service.require_registered_user(update.effective_user.id)
        except UserNotRegisteredException:
            keyboard = [
                [InlineKeyboardButton("👤 ثبت نام", callback_data="authorize")],
                [InlineKeyboardButton("هنوز مطمعن نیستم", callback_data="not_sure")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                ProductMessages.NOT_REGISTERED,
                reply_markup=reply_markup
            )
            return ConversationHandler.END
        
        # Get product details
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            await query.edit_message_text("محصول مورد نظر یافت نشد")
            return ConversationHandler.END
        
        # Store purchase context
        if context.user_data is None:
            context.user_data = {}
        context.user_data['current_product_id'] = product_id
        context.user_data['product_data'] = product
        
        # Ask about referral code
        keyboard = [
            ["کد معرف دارم"],
            ["کد معرف ندارم"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=ProductMessages.ASK_REFERRAL_CODE,
            reply_markup=reply_markup
        )
        
        return ASK_REFERRAL_CODE
    
    @handle_exceptions()
    async def handle_referral_code_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral code input from user"""
        if not update.message or not update.message.text:
            return ASK_REFERRAL_CODE
        
        user_input = update.message.text.strip()
        
        if user_input == "کد معرف دارم":
            await update.message.reply_text("لطفا کد معرف خود را وارد کنید:")
            if context.user_data is None:
                context.user_data = {}
            context.user_data['waiting_for_referral_code'] = True
            return ASK_REFERRAL_CODE
            
        elif user_input == "کد معرف ندارم":
            if context.user_data is None:
                context.user_data = {}
            context.user_data['waiting_for_referral_code'] = False
            return await self._process_order_without_referral(update, context)
            
        elif context.user_data and context.user_data.get('waiting_for_referral_code'):
            return await self._process_order_with_referral(update, context, user_input)
        
        return ASK_REFERRAL_CODE
    
    async def _process_order_with_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str):
        """Process order with referral code"""
        if not update.effective_user or not update.message:
            return ConversationHandler.END
        
        try:
            # Validate referral code
            referral = await self.referral_repository.get_by_field("code", referral_code.lower())
            
            if not referral:
                await update.message.reply_text(ProductMessages.INVALID_REFERRAL_CODE)
                return ASK_REFERRAL_CODE
            
            # Store referral data
            if context.user_data is None:
                context.user_data = {}
            context.user_data['referral'] = referral_code
            context.user_data['referral_data'] = referral
            context.user_data['waiting_for_referral_code'] = False
            
            product = context.user_data.get('product_data')
            
            # Check payment options based on product and referral
            if (product and product.grade in HIGH_SCHOOL_GRADES and 
                referral.product == ReferralCodeProductEnum.ALMAS):
                
                if referral.installment:
                    keyboard = [
                        ["پرداخت قسطی"],
                        ["پرداخت نقدی"]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                    await update.message.reply_text(
                        ProductMessages.SELECT_PAYMENT_METHOD,
                        reply_markup=reply_markup
                    )
                    return ASK_PAYMENT_METHOD
                else:
                    keyboard = [
                        ["پرداخت نقدی"],
                        ["🔙 بازگشت به منو"]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                    await update.message.reply_text(
                        ProductMessages.INSTALLMENT_OPTION_UNAVAILABLE,
                        reply_markup=reply_markup
                    )
                    return await self._ask_for_payment_proof(update, context)
            else:
                context.user_data['payment_type'] = 'cash'
                return await self._ask_for_payment_proof(update, context)
                
        except Exception as e:
            self.logger.error(f"Error processing referral code: {str(e)}")
            await update.message.reply_text(ErrorMessages.PROCESSING_ERROR)
            return ConversationHandler.END
    
    async def _process_order_without_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order without referral code"""
        if not update.effective_user or not update.message:
            return ConversationHandler.END
        
        if context.user_data is None:
            context.user_data = {}
        
        product = context.user_data.get('product_data')
        context.user_data['referral'] = None
        context.user_data['referral_data'] = None
        context.user_data['waiting_for_referral_code'] = False
        
        # Check if installment is allowed for high school grades
        if product and product.grade in HIGH_SCHOOL_GRADES:
            keyboard = [
                ["پرداخت قسطی"],
                ["پرداخت نقدی"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                ProductMessages.SELECT_PAYMENT_METHOD,
                reply_markup=reply_markup
            )
            return ASK_PAYMENT_METHOD
        else:
            context.user_data['payment_type'] = 'cash'
            return await self._ask_for_payment_proof(update, context)
    
    @handle_exceptions()
    async def handle_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment method selection"""
        if not update.message or not update.message.text:
            return ASK_PAYMENT_METHOD
        
        payment_type = update.message.text.strip()
        
        if payment_type not in ["پرداخت نقدی", "پرداخت قسطی"]:
            await update.message.reply_text("❌ لطفا یکی از گزینه‌های پرداخت را انتخاب کنید.")
            return ASK_PAYMENT_METHOD
        
        if context.user_data is None:
            context.user_data = {}
        
        context.user_data['payment_type'] = 'installment' if payment_type == "پرداخت قسطی" else 'cash'
        return await self._ask_for_payment_proof(update, context)
    
    async def _ask_for_payment_proof(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask user to send payment proof"""
        if not update.message:
            return ConversationHandler.END
        
        if context.user_data is None:
            context.user_data = {}
        
        product = context.user_data.get("product_data")
        if not product:
            await update.message.reply_text(ErrorMessages.MISSING_PRODUCT_INFO)
            return ConversationHandler.END
        
        referral = context.user_data.get("referral_data")
        
        # Final price is always the product price (no discounts)
        final_price = product.price
        is_installment = context.user_data.get('payment_type') == 'installment'
        
        # Store pricing information
        context.user_data['final_price'] = final_price
        context.user_data['first_installment'] = final_price // 2 if is_installment else final_price
        
        # Send payment instructions
        if is_installment:
            message = PaymentMessages.PAYMENT_INSTRUCTION_INSTALLMENT.format(
                config.payment.card_number,
                config.payment.card_holder_name
            )
        else:
            message = PaymentMessages.PAYMENT_INSTRUCTION_CASH.format(
                final_price,
                config.payment.card_number,
                config.payment.card_holder_name
            )
        
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        return ASK_PAYMENT_PROOF
    
    @handle_exceptions()
    async def handle_payment_proof(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment proof image upload"""
        if not update.message or not update.message.photo or not update.effective_user:
            if update.message:
                await update.message.reply_text(ErrorMessages.UPLOAD_IMAGE_ONLY)
            return ASK_PAYMENT_PROOF
        
        # Handle installment receipt upload
        if (context.user_data and 
            "upload_order_id" in context.user_data and 
            "upload_installment_index" in context.user_data):
            return await self._handle_installment_receipt(update, context)
        
        # Handle initial purchase receipt
        return await self._handle_initial_purchase_receipt(update, context)
    
    async def _handle_initial_purchase_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt for initial purchase"""
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Download and save file with error handling
        try:
            bot = context.bot
            file = await bot.get_file(file_id)
            file_path = f"receipts/receipt_{file_id}.jpg"
            os.makedirs("receipts", exist_ok=True)
            await file.download_to_drive(file_path)
        except Exception as e:
            self.logger.error(f"Error downloading file {file_id}: {str(e)}")
            await update.message.reply_text("❌ خطا در دریافت فایل. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
        
        try:
            # Get user
            user = await self.user_service.require_registered_user(update.effective_user.id)
            
            # Get order data from context with safety checks
            if not context.user_data:
                await update.message.reply_text(ErrorMessages.ORDER_DATA_INCOMPLETE)
                return ConversationHandler.END
                
            product = context.user_data.get("product_data")
            referral = context.user_data.get("referral_data")
            final_price = context.user_data.get("final_price")
            is_installment = context.user_data.get("payment_type") == "installment"
            
            if not product or final_price is None:
                await update.message.reply_text(ErrorMessages.ORDER_DATA_INCOMPLETE)
                return ConversationHandler.END
            
            # Create file record with error handling
            try:
                file_record = await self.file_repository.create(
                    file_id=file_id,
                    path=file_path
                )
            except Exception as e:
                self.logger.error(f"Error creating file record: {str(e)}")
                await update.message.reply_text("❌ خطا در ثبت اطلاعات فایل. لطفا دوباره تلاش کنید.")
                return ConversationHandler.END
            
            # Create order with seller linking (no discounts)
            try:
                seller_id = referral.owner_id if referral else None
                order = await self.order_repository.create(
                    user_id=user.id,
                    product_id=product.id,
                    status=OrderStatusEnum.PENDING,
                    seller_id=seller_id,  # Link to seller for tracking
                    final_price=final_price,  # Always equals product.price
                    installment=is_installment,
                    referral_code=referral.code if referral else None
                )
            except Exception as e:
                self.logger.error(f"Error creating order: {str(e)}")
                await update.message.reply_text("❌ خطا در ثبت سفارش. لطفا دوباره تلاش کنید.")
                return ConversationHandler.END
            
            # Associate receipt with order (this would need proper many-to-many handling)
            
            # Send success message
            await update.message.reply_text(ProductMessages.ORDER_SUCCESS)
            
            # Send notification to admin
            try:
                await self.notification_service.send_order_notification(
                    order_id=order.id,
                    user_id=user.telegram_id,
                    username=user.username,
                    product_name=product.name,
                    final_price=final_price,
                    payment_type="installment" if is_installment else "cash",
                    referral_code=referral.code if referral else None
                )
            except Exception as e:
                self.logger.error(f"Failed to send order notification: {str(e)}")
            
            self.logger.info(f"Order created: {order.id} for user {user.telegram_id}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error creating order: {str(e)}")
            await update.message.reply_text(ErrorMessages.PROCESSING_ERROR)
            return ConversationHandler.END
    
    async def _handle_installment_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt upload for installment payment"""
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Get installment context with safety checks
        if not context.user_data or "upload_order_id" not in context.user_data:
            await update.message.reply_text("❌ خطا در اطلاعات قسط. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
            
        order_id = context.user_data["upload_order_id"]
        installment_index = context.user_data["upload_installment_index"]
        
        # Download and save file with error handling
        try:
            bot = context.bot
            file = await bot.get_file(file_id)
            file_path = f"receipts/receipt_{file_id}.jpg"
            os.makedirs("receipts", exist_ok=True)
            await file.download_to_drive(file_path)
        except Exception as e:
            self.logger.error(f"Error downloading installment file {file_id}: {str(e)}")
            await update.message.reply_text("❌ خطا در دریافت فایل. لطفا دوباره تلاش کنید.")
            return ConversationHandler.END
        
        try:
            # Get order
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                await update.message.reply_text(InstallmentMessages.ORDER_NOT_FOUND)
                return ConversationHandler.END
            
            # Create file record
            file_record = await self.file_repository.create(
                file_id=file_id,
                path=file_path,
                filename=f"installment_{order_id}_{installment_index}_{file_id}.jpg",
                file_type="image/jpeg"
            )
            
            # Mark installment as paid
            order.mark_installment_paid(installment_index)
            await self.order_repository.update(order.id, **order.to_dict())
            
            await update.message.reply_text(
                InstallmentMessages.RECEIPT_UPLOADED.format(installment_index)
            )
            
            # Send notification to admin
            try:
                user = await self.user_service.get_user_by_telegram_id(update.effective_user.id)
                product = await self.product_repository.get_by_id(order.product_id)
                
                if user and product:
                    await self.notification_service.send_installment_notification(
                        order_id=order.id,
                        installment_index=installment_index,
                        user_id=user.telegram_id,
                        username=user.username,
                        product_name=product.name
                    )
            except Exception as e:
                self.logger.error(f"Failed to send installment notification: {str(e)}")
            
            # Clear context
            del context.user_data["upload_order_id"]
            del context.user_data["upload_installment_index"]
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error handling installment receipt: {str(e)}")
            await update.message.reply_text(ErrorMessages.PROCESSING_ERROR)
            return ConversationHandler.END
    
    @handle_exceptions()
    async def my_installments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's installment orders"""
        if not update.message or not update.effective_user:
            return
        
        try:
            user = await self.user_service.require_registered_user(update.effective_user.id)
            
            # Get installment orders
            orders = await self.order_repository.find(user_id=user.id, installment=True)
            
            if not orders:
                await update.message.reply_text(InstallmentMessages.NO_INSTALLMENTS)
                return
            
            # Create keyboard with orders
            keyboard = []
            for order in orders:
                product = await self.product_repository.get_by_id(order.product_id)
                if product:
                    keyboard.append([
                        InlineKeyboardButton(
                            product.name, 
                            callback_data=f"my_installment_{order.id}"
                        )
                    ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                InstallmentMessages.SELECT_PRODUCT,
                reply_markup=reply_markup
            )
            
        except UserNotRegisteredException:
            await update.message.reply_text("ابتدا باید ثبت‌نام کنید.")
    
    @handle_exceptions()
    async def handle_my_installment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle specific installment order selection"""
        if not update.callback_query:
            return
        
        query = update.callback_query
        await query.answer()
        
        try:
            order_id = int(query.data.split("_")[2])
        except (IndexError, ValueError):
            await query.edit_message_text("خطا در خواندن اطلاعات سفارش.")
            return
        
        try:
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                await query.edit_message_text(InstallmentMessages.ORDER_NOT_FOUND)
                return
            
            product = await self.product_repository.get_by_id(order.product_id)
            if not product:
                await query.edit_message_text(InstallmentMessages.PRODUCT_NOT_FOUND_INSTALLMENT)
                return
            
            # Create installment status message
            installment_amount = order.installment_amount
            message = (
                f"💎 سفارش: {product.name}\n"
                f"💰 قیمت کل: {order.final_price:,} تومان\n"
                f"📆 تعداد اقساط: 3\n"
                f"💵 مبلغ هر قسط: {installment_amount:,} تومان\n\n"
            )
            
            # Create keyboard with installment buttons
            keyboard = []
            for i in range(1, 4):
                installment_status = order.get_installment_status(i)
                if installment_status['is_paid']:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🧾 قسط {i} - {installment_status['status_text']}", 
                            callback_data="ignore"
                        )
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🧾 قسط {i} - پرداخت نشده ❌", 
                            callback_data=f"upload_receipt_{order.id}_{i}"
                        )
                    ])
            
            keyboard.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"Error showing installment details: {str(e)}")
            await query.edit_message_text("خطا در نمایش اطلاعات قسط.")
    
    @handle_exceptions()
    async def handle_single_installment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle single installment button press"""
        if not update.callback_query:
            return
        
        query = update.callback_query
        await query.answer()
        
        # This would show individual installment details
        await query.edit_message_text("جزئیات قسط")
    
    @handle_exceptions()
    async def handle_upload_receipt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt upload button callback"""
        if not update.callback_query:
            return ConversationHandler.END
        
        query = update.callback_query
        await query.answer()
        
        try:
            if not query.data:
                await query.edit_message_text("❌ خطا در پردازش درخواست.")
                return ConversationHandler.END
            
            parts = query.data.split("_")
            if len(parts) != 4:
                await query.edit_message_text("❌ خطا در پردازش درخواست.")
                return ConversationHandler.END
            
            _, _, order_id, index = parts
            
            if context.user_data is None:
                context.user_data = {}
                
            context.user_data["upload_order_id"] = int(order_id)
            context.user_data["upload_installment_index"] = int(index)
            
            await query.edit_message_text(f"📸 لطفاً رسید قسط {index} را ارسال کنید.")
            return ASK_RECEIPT_INSTALLMENT
            
        except Exception as e:
            self.logger.error(f"Error in handle_upload_receipt_callback: {str(e)}")
            await query.edit_message_text("❌ خطا در پردازش درخواست.")
            return ConversationHandler.END
    
    @handle_exceptions()
    async def handle_receipt_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt upload in conversation"""
        return await self.handle_payment_proof(update, context)
