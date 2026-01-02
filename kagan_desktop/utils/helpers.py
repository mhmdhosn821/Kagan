"""
توابع کمکی
"""
from datetime import datetime
from typing import Optional


def format_currency(amount: float) -> str:
    """فرمت مبلغ ریالی"""
    return f"{amount:,.0f} ریال"


def format_date(date_str: Optional[str], format: str = "%Y/%m/%d") -> str:
    """فرمت تاریخ"""
    if not date_str:
        return "-"
    
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime(format)
    except:
        return date_str


def format_datetime(datetime_str: Optional[str], format: str = "%Y/%m/%d %H:%M") -> str:
    """فرمت تاریخ و زمان"""
    if not datetime_str:
        return "-"
    
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime(format)
    except:
        return datetime_str


def generate_invoice_number() -> str:
    """تولید شماره فاکتور"""
    import random
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"


def persian_number(number: str) -> str:
    """تبدیل اعداد انگلیسی به فارسی"""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    
    result = str(number)
    for i, digit in enumerate(english_digits):
        result = result.replace(digit, persian_digits[i])
    
    return result


def validate_phone(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن"""
    if not phone:
        return True
    
    # حذف فاصله و خط تیره
    phone = phone.replace(" ", "").replace("-", "")
    
    # بررسی طول
    if len(phone) != 11:
        return False
    
    # بررسی شروع با 09
    if not phone.startswith("09"):
        return False
    
    # بررسی عددی بودن
    if not phone.isdigit():
        return False
    
    return True


def validate_email(email: str) -> bool:
    """اعتبارسنجی ایمیل"""
    if not email:
        return True
    
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))
