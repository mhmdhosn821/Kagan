"""
صفحه ورود به سیستم - نسخه ساده
"""
import hashlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from database import Database


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("ورود به سیستم - Kagan ERP")
        self.setFixedSize(400, 350)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # استایل کلی پنجره
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Tahoma;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        
        # عنوان
        title = QLabel("سیستم ERP کاگان")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            padding: 20px;
        """)
        layout.addWidget(title)
        
        # فیلد نام کاربری
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.username_input.setMinimumHeight(45)
        layout.addWidget(self.username_input)
        
        # فیلد رمز عبور
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        # دکمه ورود
        login_btn = QPushButton("ورود")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری و رمز عبور را وارد کنید.")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND is_active = 1"
        result = self.db.execute_query(query, (username, password_hash))
        
        if result:
            user = dict(result[0])
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")
            self.password_input.clear()
