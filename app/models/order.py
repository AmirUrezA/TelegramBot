"""
Order Model
Purchase order management with installment support
"""

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Table, String
from sqlalchemy.types import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .base import Base, BaseModel
from .enums import OrderStatusEnum


# Many-to-many relationship between orders and files (receipts)
order_receipts = Table(
    "order_receipts",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("file_id", ForeignKey("files.id"), primary_key=True)
)


class Order(BaseModel):
    """Order model for product purchases"""
    
    __tablename__ = "orders"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    status = Column(SqlEnum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.PENDING, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=True, index=True)
    
    # Payment information
    installment = Column(Boolean, nullable=False, default=False)
    final_price = Column(Integer, nullable=False)  # Final price (same as product price)
    
    # Installment tracking
    first_installment = Column(DateTime, nullable=True)
    second_installment = Column(DateTime, nullable=True)
    third_installment = Column(DateTime, nullable=True)
    
    # Referral tracking
    referral_code = Column(String, nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    seller = relationship("Seller", back_populates="orders", lazy="select")
    receipts = relationship("File", secondary=order_receipts, back_populates="orders")
    
    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, user_id={self.user_id}, "
            f"product_id={self.product_id}, status={self.status.value})>"
        )
    
    @property
    def is_installment_complete(self) -> bool:
        """Check if all installments are paid"""
        if not self.installment:
            return True  # Cash payments are complete by definition
        
        return all([
            self.first_installment is not None,
            self.second_installment is not None,
            self.third_installment is not None
        ])
    
    @property
    def paid_installments_count(self) -> int:
        """Count number of paid installments"""
        if not self.installment:
            return 1 if self.first_installment else 0
        
        return sum([
            1 if self.first_installment else 0,
            1 if self.second_installment else 0,
            1 if self.third_installment else 0
        ])
    
    @property
    def installment_amount(self) -> int:
        """Get installment amount (for 3 installments)"""
        if not self.installment:
            return self.final_price
        return self.final_price // 3
    
    @property
    def next_installment_index(self) -> int:
        """Get the index of the next unpaid installment"""
        if not self.installment:
            return 0
        
        if not self.first_installment:
            return 1
        elif not self.second_installment:
            return 2
        elif not self.third_installment:
            return 3
        return 0  # All paid
    
    def get_installment_status(self, installment_index: int) -> dict:
        """Get status information for a specific installment"""
        installment_dates = {
            1: self.first_installment,
            2: self.second_installment,
            3: self.third_installment
        }
        
        date = installment_dates.get(installment_index)
        is_paid = date is not None
        
        return {
            'index': installment_index,
            'is_paid': is_paid,
            'paid_date': date.isoformat() if date else None,
            'amount': self.installment_amount,
            'status_text': f"✅ پرداخت شده در {date.strftime('%Y/%m/%d')}" if is_paid else "❌ پرداخت نشده"
        }
    
    def mark_installment_paid(self, installment_index: int) -> bool:
        """Mark a specific installment as paid"""
        now = datetime.utcnow()
        
        if installment_index == 1:
            self.first_installment = now
        elif installment_index == 2:
            self.second_installment = now
        elif installment_index == 3:
            self.third_installment = now
        else:
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'status': self.status.value,
            'installment': self.installment,
            'final_price': self.final_price,
            'referral_code': self.referral_code,
            'installment_amount': self.installment_amount,
            'paid_installments': self.paid_installments_count,
            'is_complete': self.is_installment_complete,
            'next_installment': self.next_installment_index,
            'first_installment': self.first_installment.isoformat() if self.first_installment else None,
            'second_installment': self.second_installment.isoformat() if self.second_installment else None,
            'third_installment': self.third_installment.isoformat() if self.third_installment else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
