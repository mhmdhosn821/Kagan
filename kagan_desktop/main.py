#!/usr/bin/env python3
"""
Kagan Desktop ERP - نقطه ورود اصلی
نصب خودکار PyQt6 در صورت عدم وجود
"""
import sys
import subprocess
import importlib.util


def check_and_install_pyqt6():
    """بررسی و نصب PyQt6 در صورت عدم وجود"""
    pyqt6_installed = importlib.util.find_spec("PyQt6") is not None
    
    if not pyqt6_installed:
        print("=" * 60)
        print("⚠️  PyQt6 نصب نیست. در حال نصب...")
        print("=" * 60)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "PyQt6-Charts"])
            print("✅ PyQt6 با موفقیت نصب شد!")
            print("=" * 60)
        except subprocess.CalledProcessError:
            print("❌ خطا در نصب PyQt6. لطفاً دستی نصب کنید:")
            print("   pip install PyQt6 PyQt6-Charts")
            sys.exit(1)
    return True


if __name__ == "__main__":
    # بررسی و نصب PyQt6
    check_and_install_pyqt6()
    
    # Import بعد از اطمینان از نصب PyQt6
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QFontDatabase
    
    from database import Database
    from ui.login import LoginWindow
    
    # ایجاد application
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی - Vazir
    font_id = QFontDatabase.addApplicationFont("assets/fonts/Vazir.ttf")
    if font_id == -1:
        # fallback به فایل قدیمی
        font_id = QFontDatabase.addApplicationFont("assets/vazir.ttf")
    
    if font_id == -1:
        # اگر فایل فونت وجود نداشت، از فونت سیستم استفاده کن
        app.setFont(QFont("Tahoma", 10))
        print("⚠️  فونت وزیر یافت نشد. از Tahoma استفاده می‌شود.")
    else:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            app.setFont(QFont(font_families[0], 11))
            print(f"✅ فونت {font_families[0]} بارگذاری شد")
    
    # تنظیم RTL
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # بارگذاری تم (روشن به عنوان پیشفرض)
    from ui.theme_switcher import ThemeSwitcher
    db_temp = Database()
    try:
        result = db_temp.execute_query("SELECT value FROM settings WHERE key = 'theme'", ())
        theme = result[0]['value'] if result else "light"
    except:
        theme = "light"
    
    ThemeSwitcher.apply_theme(app, theme)
    
    # مقداردهی اولیه دیتابیس
    db = Database()
    db.initialize()
    
    # نمایش صفحه ورود
    print("=" * 60)
    print("🚀 Kagan Desktop ERP در حال اجرا...")
    print("=" * 60)
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())
