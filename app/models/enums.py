"""
Database Enums
Centralized enum definitions for database models
"""

from enum import Enum


class GradeEnum(Enum):
    """Educational grade levels"""
    GRADE_5 = 5
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9
    GRADE_10 = 10
    GRADE_11 = 11
    GRADE_12 = 12


class MajorEnum(Enum):
    """Academic majors"""
    MATH = "math"
    SCIENCE = "science"
    LECTURE = "lecture"
    GENERAL = "general"


class OrderStatusEnum(Enum):
    """Order status values"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReferralCodeProductEnum(str, Enum):
    """Products that referral codes can be applied to"""
    ALMAS = "almas"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"
