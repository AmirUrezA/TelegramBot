"""
Lottery Models
Lottery system and user participation management
"""

from sqlalchemy import Column, String, BigInteger, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel


class Lottery(BaseModel):
    """Lottery model for managing lottery events"""
    
    __tablename__ = "lottery"
    
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    max_participants = Column(Integer, nullable=True)  # Max number of participants
    
    # Prize information
    prize_description = Column(Text, nullable=True)
    prize_value = Column(Integer, nullable=True)  # Prize value in Tomans
    
    # Lottery dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    draw_date = Column(DateTime, nullable=True)
    
    # Winner information
    winner_id = Column(Integer, ForeignKey("users_in_lottery.id"), nullable=True)
    is_drawn = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    participants = relationship("UsersInLottery", back_populates="lottery", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Lottery(id={self.id}, name='{self.name}', is_active={self.is_active})>"
    
    @property
    def participant_count(self) -> int:
        """Get total number of participants"""
        return self.participants.count()
    
    @property
    def is_full(self) -> bool:
        """Check if lottery has reached max participants"""
        if not self.max_participants:
            return False
        return self.participant_count >= self.max_participants
    
    @property
    def can_participate(self) -> bool:
        """Check if users can still participate"""
        return self.is_active and not self.is_drawn and not self.is_full
    
    @property
    def status_text(self) -> str:
        """Get lottery status in Persian"""
        if self.is_drawn:
            return "قرعه کشی انجام شده"
        elif not self.is_active:
            return "غیرفعال"
        elif self.is_full:
            return "پر شده"
        else:
            return "فعال"
    
    def get_participant_by_telegram_id(self, telegram_id: int):
        """Get participant by Telegram ID"""
        return self.participants.filter_by(telegram_id=telegram_id).first()
    
    def is_user_registered(self, telegram_id: int) -> bool:
        """Check if user is already registered for this lottery"""
        return self.get_participant_by_telegram_id(telegram_id) is not None
    
    def to_dict(self) -> dict:
        """Convert lottery to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'max_participants': self.max_participants,
            'participant_count': self.participant_count,
            'is_full': self.is_full,
            'can_participate': self.can_participate,
            'status_text': self.status_text,
            'prize_description': self.prize_description,
            'prize_value': self.prize_value,
            'is_drawn': self.is_drawn,
            'winner_id': self.winner_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'draw_date': self.draw_date.isoformat() if self.draw_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UsersInLottery(BaseModel):
    """Model for tracking lottery participants"""
    
    __tablename__ = "users_in_lottery"
    
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String, nullable=True)
    number = Column(String, nullable=False, index=True)
    lottery_id = Column(Integer, ForeignKey("lottery.id"), nullable=False, index=True)
    
    # Participant information
    full_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    # Status tracking
    is_verified = Column(Boolean, default=True, nullable=False)
    is_winner = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    lottery = relationship("Lottery", back_populates="participants")
    
    def __repr__(self) -> str:
        return (
            f"<UsersInLottery(id={self.id}, telegram_id={self.telegram_id}, "
            f"lottery_id={self.lottery_id}, is_winner={self.is_winner})>"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name for the participant"""
        if self.full_name:
            return self.full_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User_{self.telegram_id}"
    
    def mark_as_winner(self) -> None:
        """Mark participant as winner"""
        self.is_winner = True
    
    def to_dict(self) -> dict:
        """Convert lottery participant to dictionary"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'number': self.number,
            'lottery_id': self.lottery_id,
            'full_name': self.full_name,
            'city': self.city,
            'display_name': self.display_name,
            'is_verified': self.is_verified,
            'is_winner': self.is_winner,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
