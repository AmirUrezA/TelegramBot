"""
Conversation State Constants
Centralized management of conversation states for better maintainability
"""

from enum import IntEnum, auto


class RegistrationStates(IntEnum):
    """User registration conversation states"""
    ASK_NAME = auto()
    ASK_CITY = auto()
    ASK_AREA = auto()
    ASK_ID = auto()
    ASK_PHONE = auto()
    ASK_OTP = auto()


class PurchaseStates(IntEnum):
    """Product purchase conversation states"""
    ASK_REFERRAL_CODE = 100
    ASK_PAYMENT_METHOD = auto()
    ASK_PAYMENT_PROOF = auto()


class CRMStates(IntEnum):
    """CRM consultation conversation states"""
    ASK_CRM_PHONE = 200
    ASK_CRM_OTP = auto()


class InstallmentStates(IntEnum):
    """Installment receipt upload states"""
    ASK_RECEIPT_INSTALLMENT = 300


class CooperationStates(IntEnum):
    """Cooperation application conversation states"""
    ASK_COOPERATION_PHONE = 400
    ASK_COOPERATION_OTP = auto()
    ASK_COOPERATION_CITY = auto()
    ASK_COOPERATION_RESUME = auto()


class LotteryStates(IntEnum):
    """Lottery participation conversation states"""
    ASK_LOTTERY = 500
    ASK_LOTTERY_NUMBER = auto()
    ASK_LOTTERY_OTP = auto()


# Legacy constants for backward compatibility
(ASK_NAME, ASK_CITY, ASK_AREA, ASK_ID, ASK_PHONE, ASK_OTP) = range(6)
ASK_REFERRAL_CODE, ASK_PAYMENT_METHOD, ASK_PAYMENT_PROOF = range(100, 103)
ASK_CRM_PHONE, ASK_CRM_OTP = range(200, 202)
ASK_RECEIPT_INSTALLMENT = range(300, 301)
ASK_COOPERATION_PHONE, ASK_COOPERATION_OTP, ASK_COOPERATION_CITY, ASK_COOPERATION_RESUME = range(400, 404)
ASK_LOTTERY, ASK_LOTTERY_NUMBER, ASK_LOTTERY_OTP = range(500, 503)
