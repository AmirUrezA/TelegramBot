from random import choice
from sqlalchemy import Column, Integer, String, DateTime, Boolean
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
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime, default=datetime.now)
