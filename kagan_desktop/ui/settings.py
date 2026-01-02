"""
صفحه تنظیمات
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QLineEdit, QDialog, QFormLayout, QFileDialog
)
from PyQt6.QtGui import QFont
import shutil
from datetime import datetime


class SettingsPage(QWidget):
    """صفحه تنظیمات"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("تنظیمات سیستم")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # اطلاعات کاربر
        user_section = QVBoxLayout()
        user_title = QLabel("اطلاعات کاربر")
        user_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        user_section.addWidget(user_title)
        
        user_info = QLabel(
            f"نام کاربری: {self.user['username']}\n"
            f"نام: {self.user['full_name']}\n"
            f"نقش: {self.get_role_display(self.user['role'])}"
        )
        user_info.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        user_section.addWidget(user_info)
        
        change_password_btn = QPushButton("تغییر رمز عبور")
        change_password_btn.clicked.connect(self.change_password)
        user_section.addWidget(change_password_btn)
        
        layout.addLayout(user_section)
        
        layout.addSpacing(20)
        
        # پشتیبان‌گیری
        backup_section = QVBoxLayout()
        backup_title = QLabel("پشتیبان‌گیری")
        backup_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        backup_section.addWidget(backup_title)
        
        backup_info = QLabel(
            "برای حفظ اطلاعات خود، به طور منظم از دیتابیس پشتیبان تهیه کنید."
        )
        backup_info.setStyleSheet("padding: 10px; background-color: #fff3cd; border-radius: 5px;")
        backup_section.addWidget(backup_info)
        
        backup_btn = QPushButton("💾 پشتیبان‌گیری از دیتابیس")
        backup_btn.clicked.connect(self.backup_database)
        backup_section.addWidget(backup_btn)
        
        layout.addLayout(backup_section)
        
        layout.addSpacing(20)
        
        # اطلاعات سیستم
        info_section = QVBoxLayout()
        info_title = QLabel("اطلاعات سیستم")
        info_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_section.addWidget(info_title)
        
        # آمار دیتابیس
        stats = self.get_database_stats()
        stats_text = (
            f"تعداد مشتریان: {stats['customers']}\n"
            f"تعداد کالاهای انبار: {stats['inventory']}\n"
            f"تعداد خدمات: {stats['services']}\n"
            f"تعداد محصولات: {stats['products']}\n"
            f"تعداد فاکتورها: {stats['invoices']}\n"
            f"تعداد نوبت‌ها: {stats['bookings']}"
        )
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        info_section.addWidget(stats_label)
        
        layout.addLayout(info_section)
        
        layout.addStretch()
        
        # درباره
        about_label = QLabel(
            "Kagan Desktop ERP v1.0\n"
            "سیستم مدیریت جامع آرایشگاه و کافه"
        )
        about_label.setStyleSheet("color: #7f8c8d; font-size: 10px; text-align: center;")
        about_label.setAlignment(about_label.alignment() | about_label.alignment())
        layout.addWidget(about_label)
        
        self.setLayout(layout)
    
    def get_role_display(self, role: str) -> str:
        """نمایش نقش به فارسی"""
        roles = {
            "admin": "مدیر",
            "barber": "آرایشگر",
            "barista": "باریستا"
        }
        return roles.get(role, role)
    
    def get_database_stats(self) -> dict:
        """دریافت آمار دیتابیس"""
        stats = {}
        
        tables = ['customers', 'inventory', 'services', 'products', 'invoices', 'bookings']
        for table in tables:
            query = f"SELECT COUNT(*) FROM {table}"
            result = self.db.execute_query(query)
            stats[table] = result[0][0] if result else 0
        
        return stats
    
    def change_password(self):
        """تغییر رمز عبور"""
        dialog = ChangePasswordDialog(self.db, self.user, self)
        dialog.exec()
    
    def backup_database(self):
        """پشتیبان‌گیری از دیتابیس"""
        try:
            # انتخاب مسیر ذخیره
            backup_name = f"kagan_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره پشتیبان",
                backup_name,
                "Database Files (*.db)"
            )
            
            if file_path:
                # کپی فایل دیتابیس
                shutil.copy2(self.db.db_path, file_path)
                QMessageBox.information(
                    self,
                    "موفق",
                    f"پشتیبان با موفقیت در مسیر زیر ذخیره شد:\n{file_path}"
                )
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در پشتیبان‌گیری: {str(e)}")


class ChangePasswordDialog(QDialog):
    """دیالوگ تغییر رمز عبور"""
    
    def __init__(self, db, user, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("تغییر رمز عبور")
        self.setMinimumWidth(350)
        
        layout = QFormLayout()
        
        # رمز فعلی
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("رمز عبور فعلی:", self.current_password)
        
        # رمز جدید
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("رمز عبور جدید:", self.new_password)
        
        # تکرار رمز جدید
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("تکرار رمز جدید:", self.confirm_password)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("تغییر رمز")
        save_btn.clicked.connect(self.change_password)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
    
    def change_password(self):
        """تغییر رمز عبور"""
        import hashlib
        
        current = self.current_password.text()
        new = self.new_password.text()
        confirm = self.confirm_password.text()
        
        if not current or not new or not confirm:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید.")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "خطا", "رمز عبور جدید و تکرار آن مطابقت ندارند.")
            return
        
        if len(new) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
        
        # بررسی رمز فعلی
        current_hash = hashlib.sha256(current.encode()).hexdigest()
        query = "SELECT id FROM users WHERE id = ? AND password = ?"
        result = self.db.execute_query(query, (self.user['id'], current_hash))
        
        if not result:
            QMessageBox.warning(self, "خطا", "رمز عبور فعلی نادرست است.")
            return
        
        # تغییر رمز
        try:
            new_hash = hashlib.sha256(new.encode()).hexdigest()
            query = "UPDATE users SET password = ? WHERE id = ?"
            self.db.execute_update(query, (new_hash, self.user['id']))
            QMessageBox.information(self, "موفق", "رمز عبور با موفقیت تغییر یافت.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تغییر رمز عبور: {str(e)}")
