"""
صفحه ورود به سیستم
"""
import hashlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from database import Database


class LoginWindow(QWidget):
    """پنجره ورود"""
    
    login_successful = pyqtSignal(dict)  # سیگنال موفقیت ورود
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("ورود به سیستم - Kagan ERP")
        self.setFixedSize(400, 500)
        
        # Layout اصلی
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # لوگو
        logo_label = QLabel()
        try:
            pixmap = QPixmap("assets/logo.png")
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        except:
            pass
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # عنوان
        title = QLabel("سیستم ERP کاگان")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("مدیریت آرایشگاه و کافه")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # فریم ورود
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        login_layout = QVBoxLayout()
        login_layout.setSpacing(15)
        
        # نام کاربری
        username_label = QLabel("نام کاربری:")
        login_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(40)
        login_layout.addWidget(self.username_input)
        
        # رمز عبور
        password_label = QLabel("رمز عبور:")
        login_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.login)
        login_layout.addWidget(self.password_input)
        
        login_frame.setLayout(login_layout)
        layout.addWidget(login_frame)
        
        layout.addSpacing(10)
        
        # دکمه ورود
        self.login_btn = QPushButton("ورود")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # اطلاعات کاربران پیشفرض
        info_label = QLabel(
            "کاربران پیشفرض:\n"
            "• مدیر: admin / admin123\n"
            "• آرایشگر: barber1 / barber123\n"
            "• باریستا: barista1 / barista123"
        )
        info_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # استایل
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
            #loginFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            #primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            #primaryButton:hover {
                background-color: #2980b9;
            }
            #primaryButton:pressed {
                background-color: #21618c;
            }
        """)
    
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
            
            # بستن پنجره ورود و باز کردن پنجره اصلی
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
