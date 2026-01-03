"""
Theme Switcher - تعویض تم روشن/تیره
"""
from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from database import Database
import os


class ThemeSwitcher(QPushButton):
    """دکمه تغییر تم"""
    
    theme_changed = pyqtSignal(str)  # Signal برای اطلاع دادن تغییر تم
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.current_theme = self.load_theme_preference()
        self.init_ui()
        
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setFixedSize(100, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button_text()
        self.clicked.connect(self.toggle_theme)
        
    def update_button_text(self):
        """بروزرسانی متن دکمه"""
        if self.current_theme == "dark":
            self.setText("🌙 تیره")
        else:
            self.setText("☀️ روشن")
    
    def load_theme_preference(self) -> str:
        """بارگذاری تنظیمات تم از دیتابیس"""
        try:
            result = self.db.execute_query(
                "SELECT value FROM settings WHERE key = 'theme'",
                ()
            )
            if result:
                return result[0]['value']
        except:
            pass
        return "light"  # پیشفرض: تم روشن
    
    def save_theme_preference(self, theme: str):
        """ذخیره تنظیمات تم در دیتابیس"""
        try:
            # بررسی وجود رکورد
            result = self.db.execute_query(
                "SELECT key FROM settings WHERE key = 'theme'",
                ()
            )
            
            if result:
                # بروزرسانی
                self.db.execute_update(
                    "UPDATE settings SET value = ? WHERE key = 'theme'",
                    (theme,)
                )
            else:
                # درج جدید
                self.db.execute_update(
                    "INSERT INTO settings (key, value) VALUES ('theme', ?)",
                    (theme,)
                )
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات تم: {e}")
    
    def toggle_theme(self):
        """تعویض بین تم روشن و تیره"""
        # تغییر تم
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        
        # ذخیره در دیتابیس
        self.save_theme_preference(self.current_theme)
        
        # بروزرسانی متن دکمه
        self.update_button_text()
        
        # ارسال سیگنال تغییر تم
        self.theme_changed.emit(self.current_theme)
    
    def get_current_theme(self) -> str:
        """دریافت تم فعلی"""
        return self.current_theme
    
    @staticmethod
    def apply_theme(app, theme: str):
        """اعمال تم به برنامه"""
        # مسیر فایل استایل
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if theme == "dark":
            style_file = os.path.join(base_dir, "assets", "styles_dark.qss")
        else:
            style_file = os.path.join(base_dir, "assets", "styles_light.qss")
        
        # بارگذاری و اعمال استایل
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            print(f"✅ تم {theme} اعمال شد")
        except FileNotFoundError:
            print(f"⚠️  فایل استایل {style_file} یافت نشد")
        except Exception as e:
            print(f"❌ خطا در اعمال تم: {e}")
