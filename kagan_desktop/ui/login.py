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
        self.setFixedSize(480, 600)
        
        # Layout اصلی
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)
        
        # لوگو
        logo_label = QLabel("🏪")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_font = QFont()
        logo_font.setPointSize(48)
        logo_label.setFont(logo_font)
        layout.addWidget(logo_label)
        
        # عنوان
        title = QLabel("سیستم ERP کاگان")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("titleLabel")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("مدیریت آرایشگاه و کافه")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitleLabel")
        subtitle_font = QFont()
        subtitle_font.setPointSize(13)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # فریم ورود
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        login_layout = QVBoxLayout()
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(30, 30, 30, 30)
        
        # نام کاربری
        username_label = QLabel("نام کاربری")
        username_label.setObjectName("fieldLabel")
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        username_label.setFont(label_font)
        login_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(50)
        input_font = QFont()
        input_font.setPointSize(12)
        self.username_input.setFont(input_font)
        login_layout.addWidget(self.username_input)
        
        # رمز عبور
        password_label = QLabel("رمز عبور")
        password_label.setObjectName("fieldLabel")
        password_label.setFont(label_font)
        login_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setFont(input_font)
        self.password_input.returnPressed.connect(self.login)
        login_layout.addWidget(self.password_input)
        
        login_frame.setLayout(login_layout)
        layout.addWidget(login_frame)
        
        layout.addSpacing(15)
        
        # دکمه ورود
        self.login_btn = QPushButton("ورود به سیستم")
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setObjectName("primaryButton")
        btn_font = QFont()
        btn_font.setPointSize(14)
        btn_font.setBold(True)
        self.login_btn.setFont(btn_font)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # اطلاعات کاربران پیشفرض
        info_label = QLabel(
            "کاربران پیشفرض:\n"
            "• مدیر: admin / admin123\n"
            "• آرایشگر: barber1 / barber123\n"
            "• باریستا: barista1 / barista123"
        )
        info_label.setObjectName("infoLabel")
        info_font = QFont()
        info_font.setPointSize(10)
        info_label.setFont(info_font)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # استایل Glass Morphism
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            #titleLabel {
                color: white;
            }
            #subtitleLabel {
                color: rgba(255, 255, 255, 0.9);
            }
            #loginFrame {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
            }
            #fieldLabel {
                color: white;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                color: white;
                font-size: 13px;
                selection-background-color: rgba(255, 255, 255, 0.3);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            QLineEdit:focus {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            #primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            #primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43a3f5, stop:1 #00dae5);
            }
            #primaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3899ec, stop:1 #00c8dc);
            }
            #infoLabel {
                color: rgba(255, 255, 255, 0.7);
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
