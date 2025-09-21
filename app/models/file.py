"""
File Model
File upload and receipt management
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel
from .order import order_receipts


class File(BaseModel):
    """File model for storing uploaded files (receipts, documents)"""
    
    __tablename__ = "files"
    
    file_id = Column(String, nullable=False, unique=True, index=True)  # Telegram file ID
    path = Column(String, nullable=False)  # Local file path
    filename = Column(String, nullable=True)  # Original filename
    file_type = Column(String, nullable=True)  # MIME type
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Relationships
    orders = relationship("Order", secondary=order_receipts, back_populates="receipts")
    
    def __repr__(self) -> str:
        return f"<File(id={self.id}, file_id='{self.file_id}', path='{self.path}')>"
    
    @property
    def file_extension(self) -> str:
        """Get file extension from path"""
        if self.path:
            return self.path.split('.')[-1].lower()
        return ""
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image"""
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
        return self.file_extension in image_extensions
    
    @property
    def formatted_size(self) -> str:
        """Get formatted file size"""
        if not self.file_size:
            return "Unknown"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def to_dict(self) -> dict:
        """Convert file to dictionary"""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'path': self.path,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'formatted_size': self.formatted_size,
            'file_extension': self.file_extension,
            'is_image': self.is_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
