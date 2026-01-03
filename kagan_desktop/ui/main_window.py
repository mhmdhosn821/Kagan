"""
پنجره اصلی با منوی کناری و زیرمنوهای تاشو
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database import Database


class CollapsibleMenu(QWidget):
    """ویجت منوی تاشو"""
    
    menu_clicked = pyqtSignal(int)  # سیگنال برای کلیک روی آیتم منو
    
    def __init__(self, title: str, icon: str, items: list):
        """
        items: لیست از تاپل‌های (نام، شماره صفحه)
        """
        super().__init__()
        self.title = title
        self.icon = icon
        self.items = items
        self.is_expanded = False
        self.submenu_buttons = []
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # دکمه اصلی
        self.main_btn = QPushButton(f"{self.icon} {self.title} ▼")
        self.main_btn.setObjectName("menuButton")
        self.main_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_btn.clicked.connect(self.toggle)
        layout.addWidget(self.main_btn)
        
        # کانتینر زیرمنو
        self.submenu_container = QWidget()
        self.submenu_container.setObjectName("submenuContainer")
        submenu_layout = QVBoxLayout()
        submenu_layout.setSpacing(0)
        submenu_layout.setContentsMargins(0, 0, 0, 0)
        
        for item_name, page_index in self.items:
            btn = QPushButton(f"    {item_name}")
            btn.setObjectName("submenuButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=page_index: self.menu_clicked.emit(idx))
            submenu_layout.addWidget(btn)
            self.submenu_buttons.append(btn)
        
        self.submenu_container.setLayout(submenu_layout)
        self.submenu_container.setVisible(False)
        layout.addWidget(self.submenu_container)
        
        self.setLayout(layout)
    
    def toggle(self):
        """تغییر وضعیت باز/بسته"""
        self.is_expanded = not self.is_expanded
        self.submenu_container.setVisible(self.is_expanded)
        arrow = "▲" if self.is_expanded else "▼"
        self.main_btn.setText(f"{self.icon} {self.title} {arrow}")
    
    def expand(self):
        """باز کردن منو"""
        if not self.is_expanded:
            self.toggle()
    
    def collapse(self):
        """بستن منو"""
        if self.is_expanded:
            self.toggle()


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
    
    def create_sidebar(self) -> QWidget:
        """ایجاد منوی کناری با زیرمنوهای تاشو"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        
        # ScrollArea برای منو
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # لوگو و عنوان
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🏪 کاگان ERP")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        user_label = QLabel(f"👤 {self.user['full_name']}")
        user_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px;")
        header_layout.addWidget(user_label)
        
        role_label = QLabel(f"نقش: {self.get_role_display(self.user['role'])}")
        role_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px;")
        header_layout.addWidget(role_label)
        
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        layout.addWidget(line)
        
        # دکمه داشبورد
        dashboard_btn = QPushButton("📊 داشبورد")
        dashboard_btn.setObjectName("sidebarButton")
        dashboard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dashboard_btn.clicked.connect(lambda: self.switch_page(0))
        layout.addWidget(dashboard_btn)
        self.menu_buttons = [dashboard_btn]
        
        # لیست منوهای تاشو
        self.collapsible_menus = []
        
        # منوی آرایشگاه
        if self.user['role'] in ['admin', 'barber']:
            barbershop_items = [
                ("داشبورد آرایشگاه", 3),
                ("خدمات", 13),
                ("آرایشگران", 14),
                ("نوبتدهی", 5),
                ("فاکتور آرایشگاه", 6),
                ("گزارش عملکرد", 15),
            ]
            barbershop_menu = CollapsibleMenu("آرایشگاه", "💇", barbershop_items)
            barbershop_menu.menu_clicked.connect(self.switch_page)
            layout.addWidget(barbershop_menu)
            self.collapsible_menus.append(barbershop_menu)
        
        # منوی کافهبار
        if self.user['role'] in ['admin', 'barista']:
            cafe_items = [
                ("داشبورد کافه", 4),
                ("محصولات", 16),
                ("باریستاها", 17),
                ("فاکتور کافه", 6),
                ("دستور ساخت", 18),
            ]
            cafe_menu = CollapsibleMenu("کافهبار", "☕", cafe_items)
            cafe_menu.menu_clicked.connect(self.switch_page)
            layout.addWidget(cafe_menu)
            self.collapsible_menus.append(cafe_menu)
        
        # منوی انبار
        if self.user['role'] == 'admin':
            inventory_items = [
                ("انبار کافه", 2),
                ("انبار آرایشگاه", 2),
                ("هشدار موجودی", 19),
                ("سفارش خرید", 20),
            ]
            inventory_menu = CollapsibleMenu("انبار", "📦", inventory_items)
            inventory_menu.menu_clicked.connect(self.switch_page)
            layout.addWidget(inventory_menu)
            self.collapsible_menus.append(inventory_menu)
        
        # خط جداکننده
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 10px 0;")
        layout.addWidget(line2)
        
        # منوهای دیگر
        other_menus = []
        if self.user['role'] in ['admin', 'barber', 'barista']:
            other_menus.append(("👥", "مشتریان", 1))
        if self.user['role'] == 'admin':
            other_menus.extend([
                ("📈", "گزارشات", 7),
                ("💰", "صندوق", 10),
                ("💵", "هزینهها", 9),
                ("👨‍💼", "پرسنل", 11),
                ("📱", "پیامک", 12),
                ("⚙️", "تنظیمات", 8),
            ])
        
        for icon, text, page_index in other_menus:
            btn = QPushButton(f"{icon} {text}")
            btn.setObjectName("sidebarButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        layout.addStretch()
        
        # دکمه خروج
        logout_btn = QPushButton("🚪 خروج")
        logout_btn.setObjectName("logoutButton")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        scroll_content.setLayout(layout)
        scroll.setWidget(scroll_content)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(scroll)
        sidebar.setLayout(sidebar_layout)
        
        return sidebar
    
    def create_header(self) -> QWidget:
        """ایجاد هدر صفحه"""
        header = QWidget()
        header.setObjectName("header")
        layout = QHBoxLayout()
        
        self.page_title = QLabel("داشبورد")
        title_font = QFont()
        title_font.setPointSize(18)
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
        user_font = QFont()
        user_font.setPointSize(12)
        user_info.setFont(user_font)
        user_info.setStyleSheet("color: #7f8c8d;")
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
        from ui.barbers import BarbersPage
        from ui.baristas import BaristasPage
        from ui.barber_report import BarberReportPage
        
        # افزودن صفحات
        self.pages.addWidget(DashboardPage(self.db, self.user))  # 0 - داشبورد
        self.pages.addWidget(CustomersPage(self.db, self.user))  # 1 - مشتریان
        self.pages.addWidget(InventoryPage(self.db, self.user))  # 2 - انبار
        self.pages.addWidget(BarbershopPage(self.db, self.user))  # 3 - آرایشگاه
        self.pages.addWidget(CafePage(self.db, self.user))  # 4 - کافه
        self.pages.addWidget(BookingPage(self.db, self.user))  # 5 - نوبتدهی
        self.pages.addWidget(InvoicesPage(self.db, self.user))  # 6 - فاکتور
        self.pages.addWidget(ReportsPage(self.db, self.user))  # 7 - گزارشات
        self.pages.addWidget(SettingsPage(self.db, self.user))  # 8 - تنظیمات
        self.pages.addWidget(ExpensesPage(self.db, self.user))  # 9 - هزینهها
        self.pages.addWidget(CashboxPage(self.db, self.user))  # 10 - صندوق
        self.pages.addWidget(StaffPage(self.db, self.user))  # 11 - پرسنل
        self.pages.addWidget(SMSPanelPage(self.db, self.user))  # 12 - پیامک
        
        # صفحات جدید برای زیرمنوها
        self.pages.addWidget(BarbershopPage(self.db, self.user))  # 13 - خدمات (استفاده از صفحه آرایشگاه)
        self.pages.addWidget(BarbersPage(self.db, self.user))  # 14 - آرایشگران
        self.pages.addWidget(BarberReportPage(self.db, self.user))  # 15 - گزارش عملکرد
        self.pages.addWidget(CafePage(self.db, self.user))  # 16 - محصولات (استفاده از صفحه کافه)
        self.pages.addWidget(BaristasPage(self.db, self.user))  # 17 - باریستاها
        self.pages.addWidget(CafePage(self.db, self.user))  # 18 - دستور ساخت (استفاده از صفحه کافه)
        self.pages.addWidget(InventoryPage(self.db, self.user))  # 19 - هشدار موجودی
        self.pages.addWidget(InventoryPage(self.db, self.user))  # 20 - سفارش خرید
        
        # تنظیم صفحه اول
        self.switch_page(0)
    
    def switch_page(self, index: int):
        """تغییر صفحه"""
        self.pages.setCurrentIndex(index)
        
        # بروزرسانی دکمه‌های منو
        for btn in self.menu_buttons:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # بروزرسانی عنوان
        page_titles = {
            0: "داشبورد",
            1: "مدیریت مشتریان",
            2: "مدیریت انبار",
            3: "بخش آرایشگاه",
            4: "بخش کافه",
            5: "نوبتدهی",
            6: "فاکتورزنی",
            7: "گزارشات",
            8: "تنظیمات",
            9: "مدیریت هزینه‌های جاری",
            10: "مدیریت صندوق",
            11: "مدیریت کارکرد پرسنل",
            12: "پنل مدیریت پیامک",
            13: "خدمات آرایشگاه",
            14: "مدیریت آرایشگران",
            15: "گزارش عملکرد آرایشگران",
            16: "محصولات کافه",
            17: "مدیریت باریستاها",
            18: "دستور ساخت محصولات",
            19: "هشدار موجودی",
            20: "سفارش خرید",
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
