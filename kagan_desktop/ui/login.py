"""
صفحه ورود به سیستم - نسخه بازنویسی شده
"""
import hashlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QPainter
from database import Database


class LoginWindow(QWidget):
    """پنجره ورود"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("ورود به سیستم - Kagan ERP")
        self.setFixedSize(500, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Layout اصلی
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        
        # فضای بالا
        main_layout.addSpacing(20)
        
        # ===== لوگو =====
        logo_label = QLabel("🏪")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 64px; background: transparent;")
        main_layout.addWidget(logo_label)
        
        # ===== عنوان =====
        title_label = QLabel("سیستم ERP کاگان")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            background: transparent;
            padding: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # ===== زیرعنوان =====
        subtitle_label = QLabel("مدیریت آرایشگاه و کافه")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: rgba(255, 255, 255, 0.85);
            background: transparent;
            padding-bottom: 20px;
        """)
        main_layout.addWidget(subtitle_label)
        
        # ===== فریم فرم لاگین =====
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        # ----- لیبل نام کاربری -----
        username_label = QLabel("👤  نام کاربری")
        username_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: white;
            background: transparent;
            padding: 5px 0;
        """)
        form_layout.addWidget(username_label)
        
        # ----- فیلد نام کاربری -----
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری را وارد کنید...")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 15px;
                font-size: 15px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.username_input.setMinimumHeight(50)
        self.username_input.setVisible(True)
        form_layout.addWidget(self.username_input)
        
        # ----- فاصله -----
        form_layout.addSpacing(10)
        
        # ----- لیبل رمز عبور -----
        password_label = QLabel("🔒  رمز عبور")
        password_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: white;
            background: transparent;
            padding: 5px 0;
        """)
        form_layout.addWidget(password_label)
        
        # ----- فیلد رمز عبور -----
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور را وارد کنید...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 15px;
                font-size: 15px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.password_input.setMinimumHeight(50)
        self.password_input.setVisible(True)
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.password_input)
        
        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)
        
        # ===== فاصله =====
        main_layout.addSpacing(25)
        
        # ===== دکمه ورود =====
        self.login_btn = QPushButton("🚀  ورود به سیستم")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
            QPushButton:pressed {
                background-color: #4c5dc4;
            }
        """)
        self.login_btn.setMinimumHeight(60)
        self.login_btn.clicked.connect(self.login)
        main_layout.addWidget(self.login_btn)
        
        # ===== فاصله =====
        main_layout.addSpacing(20)
        
        # ===== اطلاعات کاربران پیشفرض =====
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        info_title = QLabel("📋 کاربران پیشفرض:")
        info_title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent;")
        info_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(info_title)
        
        users_info = QLabel("مدیر: admin / admin123\nآرایشگر: barber1 / barber123\nباریستا: barista1 / barista123")
        users_info.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px; background: transparent;")
        users_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(users_info)
        
        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)
        
        # ===== فضای پایین =====
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def paintEvent(self, event):
        """رسم پسزمینه گرادیانت"""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        painter.fillRect(self.rect(), QBrush(gradient))
        painter.end()
        super().paintEvent(event)
    
    def login(self):
        """انجام ورود"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری و رمز عبور را وارد کنید.")
            return
        
        # هش کردن پسورد
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # بررسی کاربر
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND is_active = 1"
        result = self.db.execute_query(query, (username, password_hash))
        
        if result:
            user = dict(result[0])
            self.current_user = user
            
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(
                self,
                "خطای ورود",
                "نام کاربری یا رمز عبور اشتباه است."
            )
            self.password_input.clear()
            self.password_input.setFocus()
