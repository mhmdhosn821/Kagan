"""
پنجره اصلی با منوی کناری
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import Database


class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle(f"Kagan ERP - {self.user['full_name']}")
        self.setMinimumSize(1200, 700)
        
        # Widget اصلی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout اصلی افقی
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # محتوای اصلی
        content_area = QWidget()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # صفحات مختلف
        self.pages = QStackedWidget()
        self.load_pages()
        content_layout.addWidget(self.pages)
        
        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area, 1)
        
        central_widget.setLayout(main_layout)
        
        # استایل کلی
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            #contentArea {
                background-color: #ecf0f1;
            }
            #sidebar {
                background-color: #2c3e50;
                min-width: 220px;
                max-width: 220px;
            }
            #sidebarButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                text-align: right;
                padding: 15px 20px;
                font-size: 13px;
            }
            #sidebarButton:hover {
                background-color: #34495e;
            }
            #sidebarButton[active="true"] {
                background-color: #3498db;
                border-right: 4px solid #2980b9;
            }
            #header {
                background-color: white;
                border-radius: 10px;
                padding: 15px 20px;
                margin-bottom: 20px;
            }
            #pageContainer {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
    
    def create_sidebar(self) -> QWidget:
        """ایجاد منوی کناری"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # لوگو و عنوان
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🏪 کاگان ERP")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        user_label = QLabel(f"👤 {self.user['full_name']}")
        user_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
        header_layout.addWidget(user_label)
        
        role_label = QLabel(f"نقش: {self.get_role_display(self.user['role'])}")
        role_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        header_layout.addWidget(role_label)
        
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #34495e;")
        layout.addWidget(line)
        
        # دکمه‌های منو
        self.menu_buttons = []
        
        menus = self.get_menu_items()
        
        for icon, text, page_index in menus:
            btn = QPushButton(f"{icon} {text}")
            btn.setObjectName("sidebarButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        layout.addStretch()
        
        # دکمه خروج
        logout_btn = QPushButton("🚪 خروج")
        logout_btn.setObjectName("sidebarButton")
        logout_btn.setStyleSheet("margin-top: 10px; border-top: 1px solid #34495e;")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def get_menu_items(self) -> list:
        """دریافت آیتم‌های منو بر اساس نقش کاربر"""
        role = self.user['role']
        
        # منوهای مشترک
        menus = [
            ("📊", "داشبورد", 0),
        ]
        
        # دسترسی‌های ادمین
        if role == "admin":
            menus.extend([
                ("👥", "مشتریان", 1),
                ("📦", "انبار", 2),
                ("💇", "آرایشگاه", 3),
                ("☕", "کافه", 4),
                ("📅", "نوبت‌دهی", 5),
                ("🧾", "فاکتور", 6),
                ("📈", "گزارشات", 7),
                ("💵", "هزینه‌ها", 9),
                ("💰", "صندوق", 10),
                ("👨‍💼", "پرسنل", 11),
                ("📱", "پیامک", 12),
                ("⚙️", "تنظیمات", 8),
            ])
        elif role == "barber":
            menus.extend([
                ("👥", "مشتریان", 1),
                ("💇", "آرایشگاه", 3),
                ("📅", "نوبت‌دهی", 5),
                ("🧾", "فاکتور", 6),
            ])
        elif role == "barista":
            menus.extend([
                ("👥", "مشتریان", 1),
                ("☕", "کافه", 4),
                ("🧾", "فاکتور", 6),
            ])
        
        return menus
    
    def create_header(self) -> QWidget:
        """ایجاد هدر صفحه"""
        header = QWidget()
        header.setObjectName("header")
        layout = QHBoxLayout()
        
        self.page_title = QLabel("داشبورد")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.page_title.setFont(title_font)
        self.page_title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        # دکمه تغییر تم
        from ui.theme_switcher import ThemeSwitcher
        self.theme_switcher = ThemeSwitcher()
        self.theme_switcher.theme_changed.connect(self.on_theme_changed)
        layout.addWidget(self.theme_switcher)
        
        # اطلاعات کاربر
        user_info = QLabel(f"خوش آمدید، {self.user['full_name']}")
        user_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(user_info)
        
        header.setLayout(layout)
        return header
    
    def load_pages(self):
        """بارگذاری صفحات مختلف"""
        from ui.dashboard import DashboardPage
        from ui.customers import CustomersPage
        from ui.inventory import InventoryPage
        from ui.barbershop import BarbershopPage
        from ui.cafe import CafePage
        from ui.booking import BookingPage
        from ui.invoices import InvoicesPage
        from ui.reports import ReportsPage
        from ui.settings import SettingsPage
        from ui.expenses import ExpensesPage
        from ui.cashbox import CashboxPage
        from ui.staff import StaffPage
        from ui.sms_panel import SMSPanelPage
        
        # افزودن صفحات
        self.pages.addWidget(DashboardPage(self.db, self.user))  # 0
        self.pages.addWidget(CustomersPage(self.db, self.user))  # 1
        self.pages.addWidget(InventoryPage(self.db, self.user))  # 2
        self.pages.addWidget(BarbershopPage(self.db, self.user))  # 3
        self.pages.addWidget(CafePage(self.db, self.user))  # 4
        self.pages.addWidget(BookingPage(self.db, self.user))  # 5
        self.pages.addWidget(InvoicesPage(self.db, self.user))  # 6
        self.pages.addWidget(ReportsPage(self.db, self.user))  # 7
        self.pages.addWidget(SettingsPage(self.db, self.user))  # 8
        self.pages.addWidget(ExpensesPage(self.db, self.user))  # 9
        self.pages.addWidget(CashboxPage(self.db, self.user))  # 10
        self.pages.addWidget(StaffPage(self.db, self.user))  # 11
        self.pages.addWidget(SMSPanelPage(self.db, self.user))  # 12
        
        # تنظیم صفحه اول
        self.switch_page(0)
    
    def switch_page(self, index: int):
        """تغییر صفحه"""
        self.pages.setCurrentIndex(index)
        
        # بروزرسانی دکمه‌های منو
        for i, btn in enumerate(self.menu_buttons):
            if i < len(self.get_menu_items()):
                menu_index = self.get_menu_items()[i][2]
                btn.setProperty("active", "true" if menu_index == index else "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        
        # بروزرسانی عنوان
        page_titles = {
            0: "داشبورد",
            1: "مدیریت مشتریان",
            2: "مدیریت انبار",
            3: "بخش آرایشگاه",
            4: "بخش کافه",
            5: "نوبت‌دهی",
            6: "فاکتورزنی",
            7: "گزارشات",
            8: "تنظیمات",
            9: "مدیریت هزینه‌های جاری",
            10: "مدیریت صندوق",
            11: "مدیریت کارکرد پرسنل",
            12: "پنل مدیریت پیامک"
        }
        self.page_title.setText(page_titles.get(index, ""))
    
    def get_role_display(self, role: str) -> str:
        """نمایش نقش به فارسی"""
        roles = {
            "admin": "مدیر",
            "barber": "آرایشگر",
            "barista": "باریستا"
        }
        return roles.get(role, role)
    
    def on_theme_changed(self, theme: str):
        """رویداد تغییر تم"""
        from PyQt6.QtWidgets import QApplication
        from ui.theme_switcher import ThemeSwitcher
        
        # اعمال تم جدید
        app = QApplication.instance()
        ThemeSwitcher.apply_theme(app, theme)
        
        print(f"✨ تم به {theme} تغییر یافت")
    
    def logout(self):
        """خروج از سیستم"""
        reply = QMessageBox.question(
            self,
            "خروج",
            "آیا مطمئن هستید که می‌خواهید از سیستم خارج شوید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from ui.login import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
