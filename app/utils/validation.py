"""
Input Validation Utilities
Centralized validation logic for consistent input handling
"""

import re
from typing import List, Optional, Tuple

from app.constants.mappings import PERSIAN_TO_ENGLISH_DIGITS, VALID_AREAS


class ValidationError(Exception):
    """Custom validation error for better error handling"""
    pass


class InputValidator:
    """Enterprise-level input validation utilities"""
    
    @staticmethod
    def normalize_persian_digits(text: str) -> str:
        """Convert Persian digits to English digits"""
        return text.translate(PERSIAN_TO_ENGLISH_DIGITS)
    
    @staticmethod
    def validate_persian_name(name: str) -> Tuple[bool, str]:
        """
        Validate Persian name input
        Returns: (is_valid, normalized_name)
        """
        if not name or not isinstance(name, str):
            return False, ""
            
        normalized_name = name.strip()
        
        # Check if it contains only Persian characters and spaces, with length constraints
        if not re.fullmatch(r"[آ-ی\s]{5,50}", normalized_name):
            return False, ""
            
        # Check for reasonable word count (2-5 words)
        words = normalized_name.split()
        if len(words) < 2 or len(words) > 5:
            return False, ""
            
        return True, normalized_name
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Validate Iranian mobile phone number
        Returns: (is_valid, normalized_phone)
        """
        if not phone or not isinstance(phone, str):
            return False, ""
            
        # Normalize Persian digits
        normalized_phone = InputValidator.normalize_persian_digits(phone.strip())
        
        # Remove any spaces, dashes, or parentheses
        normalized_phone = re.sub(r'[\s\-\(\)]', '', normalized_phone)
        
        # Check Iranian mobile number pattern (09xxxxxxxxx)
        if not re.fullmatch(r"09\d{9}", normalized_phone):
            return False, ""
            
        return True, normalized_phone
    
    @staticmethod
    def validate_national_id(national_id: str) -> Tuple[bool, str]:
        """
        Validate Iranian national ID
        Returns: (is_valid, normalized_id)
        """
        if not national_id or not isinstance(national_id, str):
            return False, ""
            
        # Normalize Persian digits
        normalized_id = InputValidator.normalize_persian_digits(national_id.strip())
        
        # Remove any spaces or dashes
        normalized_id = re.sub(r'[\s\-]', '', normalized_id)
        
        # Basic length check (10 digits)
        if len(normalized_id) != 10 or not normalized_id.isdigit():
            return False, ""
            
        # Additional validation: reject sequences like 0000000000, 1111111111
        if len(set(normalized_id)) == 1:
            return False, ""
            
        # TODO: Implement full Iranian national ID checksum validation
        return True, normalized_id
    
    @staticmethod
    def validate_area_code(area: str) -> Tuple[bool, str]:
        """
        Validate educational area code
        Returns: (is_valid, normalized_area)
        """
        if not area or not isinstance(area, str):
            return False, ""
            
        # Normalize Persian digits
        normalized_area = InputValidator.normalize_persian_digits(area.strip())
        
        # Check if it's a valid area code
        if normalized_area not in VALID_AREAS:
            return False, ""
            
        return True, normalized_area
    
    @staticmethod
    def validate_city(city: str, allowed_cities: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Validate city name
        Returns: (is_valid, normalized_city)
        """
        if not city or not isinstance(city, str):
            return False, ""
            
        normalized_city = city.strip()
        
        if len(normalized_city) < 2:
            return False, ""
            
        # Check against allowed cities if provided
        if allowed_cities and normalized_city not in allowed_cities:
            return False, ""
            
        return True, normalized_city
    
    @staticmethod
    def validate_otp(otp: str, expected_otp: str) -> Tuple[bool, str]:
        """
        Validate OTP code
        Returns: (is_valid, normalized_otp)
        """
        if not otp or not isinstance(otp, str) or not expected_otp:
            return False, ""
            
        # Normalize Persian digits
        normalized_otp = InputValidator.normalize_persian_digits(otp.strip())
        
        # Remove any spaces
        normalized_otp = re.sub(r'\s', '', normalized_otp)
        
        # Check if it matches expected OTP
        if normalized_otp != expected_otp:
            return False, ""
            
        return True, normalized_otp
    
    @staticmethod
    def validate_referral_code(referral_code: str) -> Tuple[bool, str]:
        """
        Validate referral code format
        Returns: (is_valid, normalized_code)
        """
        if not referral_code or not isinstance(referral_code, str):
            return False, ""
            
        normalized_code = referral_code.strip().lower()
        
        # Basic format validation (alphanumeric, 3-20 characters)
        if not re.fullmatch(r'[a-zA-Z0-9]{3,20}', normalized_code):
            return False, ""
            
        return True, normalized_code
    
    @staticmethod
    def validate_resume_text(resume_text: str, min_length: int = 50) -> Tuple[bool, str]:
        """
        Validate resume text
        Returns: (is_valid, normalized_text)
        """
        if not resume_text or not isinstance(resume_text, str):
            return False, ""
            
        normalized_text = resume_text.strip()
        
        if len(normalized_text) < min_length:
            return False, ""
            
        return True, normalized_text
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize general text input
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Remove excessive whitespace and limit length
        sanitized = ' '.join(text.strip().split())
        
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rsplit(' ', 1)[0] + "..."
            
        return sanitized


# Convenience functions for common validations
def is_valid_persian_name(name: str) -> bool:
    """Check if name is valid Persian name"""
    is_valid, _ = InputValidator.validate_persian_name(name)
    return is_valid


def is_valid_phone(phone: str) -> bool:
    """Check if phone number is valid"""
    is_valid, _ = InputValidator.validate_phone_number(phone)
    return is_valid


def is_valid_national_id(national_id: str) -> bool:
    """Check if national ID is valid"""
    is_valid, _ = InputValidator.validate_national_id(national_id)
    return is_valid


def is_valid_area(area: str) -> bool:
    """Check if area code is valid"""
    is_valid, _ = InputValidator.validate_area_code(area)
    return is_valid


def normalize_digits(text: str) -> str:
    """Convert Persian digits to English"""
    return InputValidator.normalize_persian_digits(text)
