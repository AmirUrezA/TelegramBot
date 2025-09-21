"""
User Model
User registration and profile management
"""

from sqlalchemy import Column, String, Boolean, BigInteger, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """User model for registered bot users"""
    
    __tablename__ = "users"
    
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    number = Column(String, nullable=False, unique=True, index=True)
    area = Column(Integer, nullable=False)
    id_number = Column(String, nullable=False, index=True)
    city = Column(String, nullable=True, default="تهران")
    approved = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    orders = relationship("Order", back_populates="user", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, approved={self.approved})>"
    
    @property
    def is_registered(self) -> bool:
        """Check if user is fully registered"""
        return (
            self.approved and
            self.number is not None and
            self.id_number is not None and
            self.area is not None
        )
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'full_name': self.full_name,
            'area': self.area,
            'city': self.city,
            'approved': self.approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
