"""
Referral Code and Seller Models
Referral system and seller management
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, BigInteger
from sqlalchemy.types import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import ReferralCodeProductEnum


class Seller(BaseModel):
    """Seller/Agent model"""
    
    __tablename__ = "sellers"
    
    name = Column(String, nullable=False)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    number = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    referral_codes = relationship("ReferralCode", back_populates="owner", lazy="dynamic")
    orders = relationship("Order", back_populates="seller", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Seller(id={self.id}, name='{self.name}', telegram_id={self.telegram_id})>"
    
    @property
    def total_sales(self) -> int:
        """Get total sales count"""
        return self.orders.count()
    
    @property
    def active_referral_codes(self):
        """Get active referral codes"""
        return self.referral_codes.filter_by(is_active=True)
    
    def to_dict(self) -> dict:
        """Convert seller to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'telegram_id': self.telegram_id,
            'is_active': self.is_active,
            'total_sales': self.total_sales,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ReferralCode(BaseModel):
    """Referral code model for seller tracking"""
    
    __tablename__ = "referral_codes"
    
    owner_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    product = Column(SqlEnum(ReferralCodeProductEnum), nullable=False, index=True)
    installment = Column(Boolean, nullable=False, default=False)
    grade = Column(Integer, nullable=True)  # Specific grade if applicable
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Usage tracking
    usage_limit = Column(Integer, nullable=True)  # Max number of uses
    current_usage = Column(Integer, default=0, nullable=False)
    
    # Relationships
    owner = relationship("Seller", back_populates="referral_codes")
    
    def __repr__(self) -> str:
        return (
            f"<ReferralCode(id={self.id}, code='{self.code}', "
            f"product={self.product.value}, seller_id={self.owner_id})>"
        )
    
    @property
    def is_available(self) -> bool:
        """Check if referral code is available for use"""
        if not self.is_active:
            return False
        
        if self.usage_limit and self.current_usage >= self.usage_limit:
            return False
        
        return True
    
    @property
    def remaining_uses(self) -> int:
        """Get remaining number of uses"""
        if not self.usage_limit:
            return -1  # Unlimited
        
        return max(0, self.usage_limit - self.current_usage)
    
    @property
    def seller_name(self) -> str:
        """Get seller name for tracking"""
        return self.owner.name if self.owner else "Unknown"
    
    def increment_usage(self) -> bool:
        """Increment usage counter"""
        if not self.is_available:
            return False
        
        self.current_usage += 1
        return True
    
    def to_dict(self) -> dict:
        """Convert referral code to dictionary"""
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'code': self.code,
            'product': self.product.value,
            'installment': self.installment,
            'grade': self.grade,
            'is_active': self.is_active,
            'usage_limit': self.usage_limit,
            'current_usage': self.current_usage,
            'remaining_uses': self.remaining_uses,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
