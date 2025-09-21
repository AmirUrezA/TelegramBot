"""
Database Models Module
Enterprise-level data models with proper relationships and validation
"""

# Import base and enums first
from .base import Base
from .enums import GradeEnum, MajorEnum, OrderStatusEnum, ReferralCodeProductEnum

# Import models in dependency order
from .user import User
from .product import Product
from .referral import ReferralCode, Seller
from .file import File
from .order import Order, order_receipts
from .crm import CRM
from .lottery import Lottery, UsersInLottery
from .cooperation import Cooperation

__all__ = [
    'Base',
    'GradeEnum', 'MajorEnum', 'OrderStatusEnum', 'ReferralCodeProductEnum',
    'User', 'Product', 'Order', 'ReferralCode', 'Seller', 'File', 'CRM',
    'Lottery', 'UsersInLottery', 'Cooperation', 'order_receipts'
]
