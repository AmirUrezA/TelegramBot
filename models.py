from random import choice
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text, BigInteger
from datetime import date, datetime
from sqlalchemy.orm import ONETOMANY, relationship, declarative_base
from sqlalchemy.types import Enum as SqlEnum
from enum import Enum

Base = declarative_base()

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

class ReferralCodeProductEnum(str, Enum):
    ALMAS = "almas"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"

# Table for Many-to-Many between orders and files
order_receipts = Table(
    "order_receipts",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("file_id", ForeignKey("files.id"), primary_key=True)
)

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
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=False)
    number = Column(String, nullable=False, unique=True)
    area = Column(Integer, nullable=False)
    id_number = Column(String, nullable=False)
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
    installment = Column(Boolean, nullable=False)
    first_installment = Column(DateTime, nullable=True)
    second_installment = Column(DateTime, nullable=True)
    third_installment = Column(DateTime, nullable=True)
    discount = Column(Integer, default=0)
    final_price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime, default=datetime.now)
    receipts = relationship("File", secondary="order_receipts", back_populates="orders")

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    number = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    code = Column(String, nullable=False, unique=True)
    product = Column(SqlEnum(ReferralCodeProductEnum), nullable=False)
    installment = Column(Boolean, nullable=False)
    discount = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    file_id = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    orders = relationship("Order", secondary="order_receipts", back_populates="receipts")

class CRM(Base):
    __tablename__ = "crm"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    called = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class UsersInLottery(Base):
    __tablename__ = "users_in_lottery"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=False)
    number = Column(String, nullable=False)
    lottery_id = Column(Integer, ForeignKey("lottery.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Lottery(Base):
    __tablename__ = "lottery"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    participants = relationship("UsersInLottery", backref="lottery")

class Cooperation(Base):
    __tablename__ = "cooperation"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)