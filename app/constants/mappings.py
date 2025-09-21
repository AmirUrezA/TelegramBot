"""
Data Mapping Constants
Centralized mappings between UI text and enum values
"""

from app.models import GradeEnum, MajorEnum

# Grade mapping from Persian text to enum
GRADE_MAP = {
    "پایه پنجم": GradeEnum.GRADE_5,
    "پایه ششم": GradeEnum.GRADE_6,
    "پایه هفتم": GradeEnum.GRADE_7,
    "پایه هشتم": GradeEnum.GRADE_8,
    "پایه نهم": GradeEnum.GRADE_9,
    "پایه دهم": GradeEnum.GRADE_10,
    "پایه یازدهم": GradeEnum.GRADE_11,
    "پایه دوازدهم": GradeEnum.GRADE_12,
}

# Major mapping from Persian text to enum
MAJOR_MAP = {
    "ریاضی": MajorEnum.MATH,
    "تجربی": MajorEnum.SCIENCE,
    "انسانی": MajorEnum.LECTURE,
    "عمومی": MajorEnum.GENERAL,
}

# Menu command detection list
MENU_COMMANDS = [
    "👤 ثبت نام",
    "🎲 قرعه کشی", 
    "📚 خرید ویژه محصولات از نمایندگی 📚",
    "💡 راهنما",
    "💬 تماس با ما",
    "🔙 بازگشت به منو",
    "💎 خرید قسطی اشتراک الماس 💎",
    "💳 اقساط من",
    "💬 مشاوره تلفنی رایگان",
    "👩‍💻 پشتیبانی",
    "🤝 همکاری با نمایندگی"
]

# Digit conversion mapping
PERSIAN_TO_ENGLISH_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

# Valid area codes
VALID_AREAS = {"1", "2", "3"}

# High school grades that require major selection
HIGH_SCHOOL_GRADES = {GradeEnum.GRADE_10, GradeEnum.GRADE_11, GradeEnum.GRADE_12}
