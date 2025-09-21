"""
Product Model
Educational product catalog management
"""

from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.types import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import GradeEnum, MajorEnum


class Product(BaseModel):
    """Product model for educational materials"""
    
    __tablename__ = "products"
    
    name = Column(String, nullable=False, unique=True, index=True)
    grade = Column(SqlEnum(GradeEnum), nullable=False, index=True)
    major = Column(SqlEnum(MajorEnum), nullable=False, index=True)
    description = Column(Text)
    price = Column(Integer, nullable=False)  # Price in Tomans
    image = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)  # For soft deletion
    
    # Relationships
    orders = relationship("Order", back_populates="product", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', grade={self.grade.name}, price={self.price})>"
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price string"""
        return f"{self.price:,} تومان"
    
    @property
    def grade_persian(self) -> str:
        """Get Persian grade name"""
        grade_mapping = {
            GradeEnum.GRADE_5: "پایه پنجم",
            GradeEnum.GRADE_6: "پایه ششم",
            GradeEnum.GRADE_7: "پایه هفتم",
            GradeEnum.GRADE_8: "پایه هشتم",
            GradeEnum.GRADE_9: "پایه نهم",
            GradeEnum.GRADE_10: "پایه دهم",
            GradeEnum.GRADE_11: "پایه یازدهم",
            GradeEnum.GRADE_12: "پایه دوازدهم",
        }
        return grade_mapping.get(self.grade, str(self.grade.value))
    
    @property
    def major_persian(self) -> str:
        """Get Persian major name"""
        major_mapping = {
            MajorEnum.MATH: "ریاضی",
            MajorEnum.SCIENCE: "تجربی",
            MajorEnum.LECTURE: "انسانی",
            MajorEnum.GENERAL: "عمومی",
        }
        return major_mapping.get(self.major, self.major.value)
    
    def to_dict(self) -> dict:
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'grade': self.grade.value,
            'grade_persian': self.grade_persian,
            'major': self.major.value,
            'major_persian': self.major_persian,
            'description': self.description,
            'price': self.price,
            'formatted_price': self.formatted_price,
            'image': self.image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
