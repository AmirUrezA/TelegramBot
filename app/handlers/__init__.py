"""
Handlers Module
Telegram conversation handlers with dependency injection
"""

from .menu_handler import MenuHandler
from .registration_handler import RegistrationHandler
from .product_handler import ProductHandler
from .payment_handler import PaymentHandler
from .crm_handler import CRMHandler
from .lottery_handler import LotteryHandler
from .cooperation_handler import CooperationHandler

__all__ = [
    'MenuHandler',
    'RegistrationHandler', 
    'ProductHandler',
    'PaymentHandler',
    'CRMHandler',
    'LotteryHandler',
    'CooperationHandler'
]