"""
Notification Service Layer
Admin notification and messaging system
"""

import os
from typing import Optional
from datetime import datetime
from telethon import TelegramClient

from app.config.settings import config
from app.exceptions.base import NotificationException
from app.utils.logging import notification_logger


class NotificationService:
    """Service for sending notifications to admins and users"""
    
    def __init__(self):
        self.client = None
        self.admin_username = config.telegram.admin_username
    
    async def _get_client(self) -> TelegramClient:
        """Get initialized Telegram client"""
        if not self.client:
            if not config.telegram.api_id or not config.telegram.api_hash:
                raise NotificationException(
                    recipient="admin",
                    message="Missing Telegram API credentials for notifications"
                )
            
            self.client = TelegramClient(
                'notification_session',
                config.telegram.api_id,
                config.telegram.api_hash
            )
            
            await self.client.start(bot_token=config.telegram.bot_token)
            notification_logger.info("Notification client initialized")
        
        return self.client
    
    async def send_to_admin(self, message: str, parse_mode: str = None) -> bool:
        """
        Send notification message to admin
        
        Args:
            message: Message text
            parse_mode: Telegram parse mode (Markdown, HTML, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            client = await self._get_client()
            target_user = await client.get_entity(f'@{self.admin_username}')
            
            await client.send_message(
                target_user,
                message,
                parse_mode=parse_mode
            )
            
            notification_logger.info(f"Admin notification sent successfully to @{self.admin_username}")
            return True
            
        except Exception as e:
            notification_logger.error(f"Failed to send admin notification: {str(e)}", exc_info=True)
            raise NotificationException(
                recipient=f"@{self.admin_username}",
                message=f"Failed to send notification: {str(e)}"
            )
    
    async def send_order_notification(
        self,
        order_id: int,
        user_id: int,
        username: str,
        product_name: str,
        final_price: int,
        payment_type: str,
        referral_code: Optional[str] = None
    ) -> bool:
        """Send new order notification to admin"""
        
        payment_type_persian = "نقدی" if payment_type == "cash" else "قسطی"
        referral_info = f"🎫 کد معرف: {referral_code}\n" if referral_code else "🎫 کد معرف: ندارد\n"
        
        message = (
            "🛒 سفارش جدید!\n\n"
            f"📦 محصول: {product_name}\n"
            f"👤 کاربر: @{username}\n" if username else f"🆔 آیدی: {user_id}\n"
            f"💰 قیمت نهایی: {final_price:,} تومان\n"
            f"💳 نوع پرداخت: {payment_type_persian}\n"
            f"{referral_info}"
            f"🆔 شماره سفارش: {order_id}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_cooperation_notification(
        self,
        telegram_id: int,
        username: str,
        phone: str,
        city: str,
        resume_text: str
    ) -> bool:
        """Send cooperation application notification to admin"""
        
        display_name = f"@{username}" if username else f"User_{telegram_id}"
        
        message = (
            "🤝 درخواست همکاری جدید!\n\n"
            f"👤 کاربر: {display_name}\n"
            f"📞 شماره: {phone}\n"
            f"🏙️ شهر: {city}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            f"📝 رزومه:\n{resume_text}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_lottery_notification(
        self,
        lottery_name: str,
        telegram_id: int,
        username: str,
        phone: str
    ) -> bool:
        """Send lottery participation notification to admin"""
        
        display_name = f"@{username}" if username else f"User_{telegram_id}"
        
        message = (
            "🎲 شرکت جدید در قرعه کشی!\n\n"
            f"🎯 قرعه کشی: {lottery_name}\n"
            f"👤 کاربر: {display_name}\n"
            f"📞 شماره: {phone}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_crm_notification(
        self,
        phone: str,
        telegram_id: int,
        username: str
    ) -> bool:
        """Send CRM consultation request notification to admin"""
        
        display_name = f"@{username}" if username else f"User_{telegram_id}"
        
        message = (
            "💬 درخواست مشاوره جدید!\n\n"
            f"👤 کاربر: {display_name}\n"
            f"📞 شماره: {phone}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "لطفاً در اسرع وقت با این کاربر تماس بگیرید.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_installment_notification(
        self,
        order_id: int,
        installment_index: int,
        user_id: int,
        username: str,
        product_name: str
    ) -> bool:
        """Send installment payment notification to admin"""
        
        display_name = f"@{username}" if username else f"User_{user_id}"
        
        message = (
            "💳 پرداخت قسط جدید!\n\n"
            f"📦 محصول: {product_name}\n"
            f"👤 کاربر: {display_name}\n"
            f"🧾 قسط شماره: {installment_index}\n"
            f"🆔 شماره سفارش: {order_id}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_registration_notification(
        self,
        user_id: int,
        telegram_id: int,
        username: str,
        full_name: str,
        phone: str,
        area: int
    ) -> bool:
        """Send user registration notification to admin"""
        
        display_name = f"@{username}" if username else f"User_{telegram_id}"
        
        message = (
            "👤 کاربر جدید ثبت نام کرد!\n\n"
            f"👤 نام: {full_name}\n"
            f"📱 کاربر: {display_name}\n"
            f"📞 شماره: {phone}\n"
            f"📍 منطقه: {area}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def send_error_notification(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[int] = None,
        context: Optional[dict] = None
    ) -> bool:
        """Send error notification to admin"""
        
        user_info = f"👤 کاربر: {user_id}\n" if user_id else ""
        context_info = ""
        
        if context:
            context_info = "🔍 جزئیات:\n"
            for key, value in context.items():
                context_info += f"• {key}: {value}\n"
            context_info += "\n"
        
        message = (
            "🚨 خطای سیستم!\n\n"
            f"📋 نوع خطا: {error_type}\n"
            f"📝 پیام: {error_message}\n"
            f"{user_info}"
            f"{context_info}"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return await self.send_to_admin(message)
    
    async def close(self) -> None:
        """Close notification client"""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            notification_logger.info("Notification client disconnected")


# Global notification service instance
notification_service = NotificationService()
