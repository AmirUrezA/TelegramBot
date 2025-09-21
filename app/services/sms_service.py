"""
SMS Service Layer
SMS sending functionality with Kavenegar integration
"""

import random
from typing import Optional, Dict, Any
from kavenegar import KavenegarAPI, APIException, HTTPException

from app.config.settings import config
from app.exceptions.base import SMSException
from app.utils.logging import logger


class SMSService:
    """Service for SMS operations using Kavenegar"""
    
    def __init__(self):
        self.api = KavenegarAPI(config.sms.kavenegar_api_key)
        self.verify_template = config.sms.verify_template
    
    def generate_otp(self, length: int = 4) -> str:
        """Generate random OTP code"""
        return str(random.randint(10**(length-1), 10**length - 1))
    
    async def send_otp(self, phone_number: str, otp: str, template: Optional[str] = None) -> dict:
        """
        Send OTP SMS using verification template
        
        Args:
            phone_number: Recipient phone number
            otp: OTP code to send
            template: Template name (defaults to configured template)
            
        Returns:
            dict: Response from SMS service
            
        Raises:
            SMSException: If SMS sending fails
        """
        try:
            template_name = template or self.verify_template
            
            response = self.api.verify_lookup({
                "receptor": phone_number,
                "token": otp,
                "template": template_name,
                "type": "sms"
            })
            
            logger.info(f"OTP sent successfully to {phone_number}")
            
            return {
                "success": True,
                "message": "OTP sent successfully",
                "response": response
            }
            
        except APIException as e:
            error_msg = f"Kavenegar API error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
        
        except HTTPException as e:
            error_msg = f"HTTP error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
    
    async def send_custom_message(
        self, 
        phone_number: str, 
        message: str, 
        sender: Optional[str] = None
    ) -> dict:
        """
        Send custom SMS message
        
        Args:
            phone_number: Recipient phone number
            message: Message text
            sender: Sender number (optional)
            
        Returns:
            dict: Response from SMS service
            
        Raises:
            SMSException: If SMS sending fails
        """
        try:
            params = {
                "receptor": phone_number,
                "message": message
            }
            
            if sender:
                params["sender"] = sender
            
            response = self.api.sms_send(params)
            
            logger.info(f"Custom SMS sent successfully to {phone_number}")
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "response": response
            }
            
        except APIException as e:
            error_msg = f"Kavenegar API error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
        
        except HTTPException as e:
            error_msg = f"HTTP error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, extra={"phone": phone_number, "error": str(e)})
            raise SMSException(
                phone_number=phone_number,
                error_details=error_msg
            )
    
    async def send_bulk_sms(
        self, 
        phone_numbers: list, 
        message: str, 
        sender: Optional[str] = None
    ) -> dict:
        """
        Send bulk SMS to multiple recipients
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: Message text
            sender: Sender number (optional)
            
        Returns:
            dict: Response from SMS service
            
        Raises:
            SMSException: If SMS sending fails
        """
        if not phone_numbers:
            raise SMSException(
                phone_number="bulk",
                error_details="No phone numbers provided"
            )
        
        try:
            params = {
                "receptor": phone_numbers,
                "message": message
            }
            
            if sender:
                params["sender"] = sender
            
            response = self.api.sms_sendarray(params)
            
            logger.info(f"Bulk SMS sent to {len(phone_numbers)} recipients")
            
            return {
                "success": True,
                "message": f"Bulk SMS sent to {len(phone_numbers)} recipients",
                "response": response
            }
            
        except APIException as e:
            error_msg = f"Kavenegar API error: {str(e)}"
            logger.error(error_msg, extra={"phone_count": len(phone_numbers), "error": str(e)})
            raise SMSException(
                phone_number="bulk",
                error_details=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, extra={"phone_count": len(phone_numbers), "error": str(e)})
            raise SMSException(
                phone_number="bulk",
                error_details=error_msg
            )
    
    async def get_sms_status(self, message_id: str) -> dict:
        """
        Get SMS delivery status
        
        Args:
            message_id: Message ID from previous send operation
            
        Returns:
            dict: Status information
        """
        try:
            response = self.api.sms_status(message_id)
            
            return {
                "success": True,
                "status": response
            }
            
        except Exception as e:
            logger.error(f"Error getting SMS status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_valid_phone_number(self, phone_number: str) -> bool:
        """Validate Iranian phone number format"""
        from app.utils.validation import is_valid_phone
        return is_valid_phone(phone_number)


# Global SMS service instance
sms_service = SMSService()
