from random import choice
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.types import Enum as SqlEnum
from enum import Enum
from db import Base

class GradeEnum(Enum):
    GRADE_5 = 5
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9
    GRADE_10 = 10
    GRADE_11 = 11
    GRADE_12 = 12

class MajorEnum(Enum):
    MATH = "math"
    SCIENCE = "science"
    LECTURE = "lecture"
    GENERAL = "general"

class OrderStatusEnum(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    grade = Column(SqlEnum(GradeEnum), nullable=False)
    major = Column(SqlEnum(MajorEnum), nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    image = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=False)
    number = Column(String, nullable=False, unique=True)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime, default=datetime.now)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    status = Column(SqlEnum(OrderStatusEnum), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=True)
    discount = Column(Integer, default=0)
    final_price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime, default=datetime.now)

class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(Integer, nullable=False, unique=True)
    number = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    

class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False, unique=True)
    discount = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
