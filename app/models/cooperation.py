"""
Cooperation Model
Job application and cooperation request management
"""

from sqlalchemy import Column, String, BigInteger, Text, Boolean, Integer, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship

from .base import BaseModel


class Cooperation(BaseModel):
    """Cooperation model for job applications"""
    
    __tablename__ = "cooperation"
    
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String, nullable=True)
    phone_number = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    
    # Application status
    status = Column(String, default="pending", nullable=False, index=True)  # pending, reviewed, accepted, rejected
    review_notes = Column(Text, nullable=True)  # Internal review notes
    reviewer_id = Column(Integer, nullable=True)  # Who reviewed this application
    
    # Contact tracking
    contacted = Column(Boolean, default=False, nullable=False)
    contact_date = Column(DateTime, nullable=True)
    contact_notes = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return (
            f"<Cooperation(id={self.id}, telegram_id={self.telegram_id}, "
            f"status='{self.status}', city='{self.city}')>"
        )
    
    @property
    def status_text_persian(self) -> str:
        """Get status in Persian"""
        status_mapping = {
            'pending': 'در انتظار بررسی',
            'reviewed': 'بررسی شده',
            'accepted': 'پذیرفته شده',
            'rejected': 'رد شده',
            'interviewed': 'مصاحبه شده'
        }
        return status_mapping.get(self.status, self.status)
    
    @property
    def display_name(self) -> str:
        """Get display name"""
        if self.username:
            return f"@{self.username}"
        else:
            return f"User_{self.telegram_id}"
    
    @property
    def resume_excerpt(self) -> str:
        """Get resume excerpt (first 100 characters)"""
        if len(self.resume_text) <= 100:
            return self.resume_text
        return self.resume_text[:100] + "..."
    
    def update_status(self, new_status: str, notes: str = None, reviewer_id: int = None) -> bool:
        """Update application status"""
        valid_statuses = ['pending', 'reviewed', 'accepted', 'rejected', 'interviewed']
        if new_status not in valid_statuses:
            return False
        
        self.status = new_status
        if notes:
            self.review_notes = notes
        if reviewer_id:
            self.reviewer_id = reviewer_id
        
        return True
    
    def mark_contacted(self, notes: str = None) -> None:
        """Mark as contacted with optional notes"""
        self.contacted = True
        self.contact_date = datetime.utcnow()
        if notes:
            self.contact_notes = notes
    
    def to_dict(self) -> dict:
        """Convert cooperation record to dictionary"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'display_name': self.display_name,
            'phone_number': self.phone_number,
            'city': self.city,
            'resume_text': self.resume_text,
            'resume_excerpt': self.resume_excerpt,
            'status': self.status,
            'status_text': self.status_text_persian,
            'review_notes': self.review_notes,
            'reviewer_id': self.reviewer_id,
            'contacted': self.contacted,
            'contact_date': self.contact_date.isoformat() if self.contact_date else None,
            'contact_notes': self.contact_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
