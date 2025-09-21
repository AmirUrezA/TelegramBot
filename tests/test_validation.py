"""
Validation Tests
Unit tests for input validation utilities
"""

import pytest
from app.utils.validation import InputValidator


class TestInputValidator:
    """Test input validation utilities"""
    
    def test_validate_persian_name_valid(self):
        """Test valid Persian names"""
        valid_names = [
            "علی محمدی",
            "فاطمه احمدی",
            "محمد رضا پور حسنی"
        ]
        
        for name in valid_names:
            is_valid, normalized = InputValidator.validate_persian_name(name)
            assert is_valid, f"Name '{name}' should be valid"
            assert normalized == name
    
    def test_validate_persian_name_invalid(self):
        """Test invalid Persian names"""
        invalid_names = [
            "Ali",  # English
            "123",  # Numbers
            "علی123",  # Mixed
            "ا",  # Too short
            "a" * 60,  # Too long
        ]
        
        for name in invalid_names:
            is_valid, _ = InputValidator.validate_persian_name(name)
            assert not is_valid, f"Name '{name}' should be invalid"
    
    def test_validate_phone_number_valid(self):
        """Test valid phone numbers"""
        valid_phones = [
            "09123456789",
            "09987654321",
            "۰۹۱۲۳۴۵۶۷۸۹"  # Persian digits
        ]
        
        for phone in valid_phones:
            is_valid, normalized = InputValidator.validate_phone_number(phone)
            assert is_valid, f"Phone '{phone}' should be valid"
            assert normalized.startswith("09")
            assert len(normalized) == 11
    
    def test_validate_phone_number_invalid(self):
        """Test invalid phone numbers"""
        invalid_phones = [
            "123456789",  # Too short
            "081234567890",  # Wrong prefix
            "091234567890",  # Too long
            "09abcdefghi",  # Contains letters
            ""  # Empty
        ]
        
        for phone in invalid_phones:
            is_valid, _ = InputValidator.validate_phone_number(phone)
            assert not is_valid, f"Phone '{phone}' should be invalid"
    
    def test_validate_national_id_valid(self):
        """Test valid national IDs"""
        valid_ids = [
            "1234567890",
            "۱۲۳۴۵۶۷۸۹۰"  # Persian digits
        ]
        
        for national_id in valid_ids:
            is_valid, normalized = InputValidator.validate_national_id(national_id)
            assert is_valid, f"ID '{national_id}' should be valid"
            assert len(normalized) == 10
            assert normalized.isdigit()
    
    def test_validate_national_id_invalid(self):
        """Test invalid national IDs"""
        invalid_ids = [
            "123456789",  # Too short
            "12345678901",  # Too long
            "0000000000",  # All same digits
            "1111111111",  # All same digits
            "12345abcde",  # Contains letters
            ""  # Empty
        ]
        
        for national_id in invalid_ids:
            is_valid, _ = InputValidator.validate_national_id(national_id)
            assert not is_valid, f"ID '{national_id}' should be invalid"
    
    def test_validate_area_code_valid(self):
        """Test valid area codes"""
        valid_areas = ["1", "2", "3", "۱", "۲", "۳"]
        
        for area in valid_areas:
            is_valid, normalized = InputValidator.validate_area_code(area)
            assert is_valid, f"Area '{area}' should be valid"
            assert normalized in ["1", "2", "3"]
    
    def test_validate_area_code_invalid(self):
        """Test invalid area codes"""
        invalid_areas = ["0", "4", "10", "a", ""]
        
        for area in invalid_areas:
            is_valid, _ = InputValidator.validate_area_code(area)
            assert not is_valid, f"Area '{area}' should be invalid"
    
    def test_validate_otp_valid(self):
        """Test valid OTP validation"""
        is_valid, normalized = InputValidator.validate_otp("1234", "1234")
        assert is_valid
        assert normalized == "1234"
        
        # Test with Persian digits
        is_valid, normalized = InputValidator.validate_otp("۱۲۳۴", "1234")
        assert is_valid
        assert normalized == "1234"
    
    def test_validate_otp_invalid(self):
        """Test invalid OTP validation"""
        invalid_cases = [
            ("1234", "5678"),  # Wrong code
            ("12345", "1234"),  # Wrong length
            ("abc", "1234"),   # Non-numeric
            ("", "1234"),      # Empty
        ]
        
        for input_otp, expected_otp in invalid_cases:
            is_valid, _ = InputValidator.validate_otp(input_otp, expected_otp)
            assert not is_valid
    
    def test_normalize_persian_digits(self):
        """Test Persian digit normalization"""
        test_cases = [
            ("۰۱۲۳۴۵۶۷۸۹", "0123456789"),
            ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
            ("1234", "1234"),  # Already English
            ("۱۲۳abc", "123abc")  # Mixed
        ]
        
        for persian, expected in test_cases:
            result = InputValidator.normalize_persian_digits(persian)
            assert result == expected
    
    def test_sanitize_text_input(self):
        """Test text sanitization"""
        test_cases = [
            ("  hello  world  ", "hello world"),
            ("test\n\ntext", "test text"),
            ("a" * 1010, "a" * 1000 + "..."),  # Length limit
            ("", "")  # Empty
        ]
        
        for input_text, expected in test_cases:
            result = InputValidator.sanitize_text_input(input_text)
            assert result == expected
