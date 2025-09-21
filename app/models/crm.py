"""
CRM Model
Customer relationship management and consultation requests
"""

from sqlalchemy import Column, String, Boolean, Integer

from .base import BaseModel


class CRM(BaseModel):
    """CRM model for consultation requests"""
    
    __tablename__ = "crm"
    
    number = Column(String, nullable=False, index=True)
    called = Column(Boolean, default=False, nullable=False, index=True)
    notes = Column(String, nullable=True)  # Internal notes for consultation
    priority = Column(Integer, default=1, nullable=False)  # Priority level (1-5)
    
    def __repr__(self) -> str:
        return f"<CRM(id={self.id}, number='{self.number}', called={self.called})>"
    
    @property
    def status_text(self) -> str:
        """Get status text in Persian"""
        return "تماس گرفته شده" if self.called else "در انتظار تماس"
    
    @property
    def priority_text(self) -> str:
        """Get priority text in Persian"""
        priority_mapping = {
            1: "عادی",
            2: "متوسط",
            3: "مهم",
            4: "ضروری",
            5: "اورژانسی"
        }
        return priority_mapping.get(self.priority, "عادی")
    
    def mark_called(self, notes: str = None) -> None:
        """Mark as called with optional notes"""
        self.called = True
        if notes:
            self.notes = notes
    
    def set_priority(self, priority: int) -> bool:
        """Set priority level (1-5)"""
        if 1 <= priority <= 5:
            self.priority = priority
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert CRM record to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'called': self.called,
            'status_text': self.status_text,
            'notes': self.notes,
            'priority': self.priority,
            'priority_text': self.priority_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
