"""
ابزارهای تقویم شمسی (جلالی)
"""
import jdatetime
from datetime import datetime
from typing import Optional


def gregorian_to_jalali(date: datetime) -> str:
    """
    تبدیل تاریخ میلادی به شمسی
    
    Args:
        date: تاریخ میلادی
    
    Returns:
        رشته تاریخ شمسی به فرمت YYYY/MM/DD
    """
    try:
        jalali_date = jdatetime.date.fromgregorian(
            year=date.year,
            month=date.month,
            day=date.day
        )
        return jalali_date.strftime("%Y/%m/%d")
    except Exception as e:
        print(f"خطا در تبدیل تاریخ: {e}")
        return date.strftime("%Y/%m/%d")


def jalali_to_gregorian(jalali_str: str) -> Optional[datetime]:
    """
    تبدیل تاریخ شمسی به میلادی
    
    Args:
        jalali_str: رشته تاریخ شمسی به فرمت YYYY/MM/DD
    
    Returns:
        تاریخ میلادی یا None در صورت خطا
    """
    try:
        parts = jalali_str.split("/")
        if len(parts) != 3:
            return None
        
        year, month, day = map(int, parts)
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.togregorian()
    except Exception as e:
        print(f"خطا در تبدیل تاریخ شمسی: {e}")
        return None


def format_jalali_date(date: datetime, include_time: bool = False) -> str:
    """
    فرمت کردن تاریخ میلادی به شمسی با نام ماه فارسی
    
    Args:
        date: تاریخ میلادی
        include_time: آیا ساعت را نیز نمایش دهد
    
    Returns:
        تاریخ فرمت شده به فارسی
    """
    try:
        jalali_date = jdatetime.date.fromgregorian(
            year=date.year,
            month=date.month,
            day=date.day
        )
        
        # نام ماه‌های فارسی
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", 
            "مرداد", "شهریور", "مهر", "آبان",
            "آذر", "دی", "بهمن", "اسفند"
        ]
        
        month_name = month_names[jalali_date.month - 1]
        result = f"{jalali_date.day} {month_name} {jalali_date.year}"
        
        if include_time:
            result += date.strftime(" - %H:%M")
        
        return result
    except Exception as e:
        print(f"خطا در فرمت کردن تاریخ: {e}")
        return date.strftime("%Y/%m/%d" + (" %H:%M" if include_time else ""))


def get_today_jalali() -> str:
    """
    دریافت تاریخ امروز به شمسی
    
    Returns:
        تاریخ امروز به شمسی
    """
    today = datetime.now()
    return gregorian_to_jalali(today)


def get_jalali_month_name(month: int) -> str:
    """
    دریافت نام ماه شمسی به فارسی
    
    Args:
        month: شماره ماه (1-12)
    
    Returns:
        نام ماه به فارسی
    """
    month_names = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", 
        "مرداد", "شهریور", "مهر", "آبان",
        "آذر", "دی", "بهمن", "اسفند"
    ]
    
    if 1 <= month <= 12:
        return month_names[month - 1]
    return ""


def get_jalali_weekday_name(weekday: int) -> str:
    """
    دریافت نام روز هفته به فارسی
    
    Args:
        weekday: شماره روز هفته (0=شنبه, 6=جمعه)
    
    Returns:
        نام روز به فارسی
    """
    weekday_names = [
        "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه",
        "چهارشنبه", "پنج‌شنبه", "جمعه"
    ]
    
    if 0 <= weekday <= 6:
        return weekday_names[weekday]
    return ""


def parse_jalali_date(date_str: str) -> Optional[jdatetime.date]:
    """
    تجزیه رشته تاریخ شمسی
    
    Args:
        date_str: رشته تاریخ به فرمت YYYY/MM/DD یا YYYY-MM-DD
    
    Returns:
        تاریخ شمسی یا None در صورت خطا
    """
    try:
        # تبدیل - به /
        date_str = date_str.replace("-", "/")
        parts = date_str.split("/")
        
        if len(parts) != 3:
            return None
        
        year, month, day = map(int, parts)
        return jdatetime.date(year, month, day)
    except Exception as e:
        print(f"خطا در تجزیه تاریخ: {e}")
        return None


def get_jalali_date_range(start_date: datetime, end_date: datetime) -> str:
    """
    نمایش بازه تاریخ به شمسی
    
    Args:
        start_date: تاریخ شروع
        end_date: تاریخ پایان
    
    Returns:
        بازه تاریخ به فارسی
    """
    start_jalali = format_jalali_date(start_date)
    end_jalali = format_jalali_date(end_date)
    return f"{start_jalali} تا {end_jalali}"


def is_leap_year_jalali(year: int) -> bool:
    """
    بررسی سال کبیسه در تقویم شمسی
    
    Args:
        year: سال شمسی
    
    Returns:
        True اگر سال کبیسه باشد
    """
    return jdatetime.date(year, 1, 1).isleap()


def get_days_in_jalali_month(year: int, month: int) -> int:
    """
    تعداد روزهای یک ماه شمسی
    
    Args:
        year: سال شمسی
        month: ماه شمسی (1-12)
    
    Returns:
        تعداد روز
    """
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    else:  # month == 12
        return 30 if is_leap_year_jalali(year) else 29
