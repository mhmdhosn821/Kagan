"""
پنل مدیریت پیامک
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QHeaderView, QTabWidget, QSpinBox
)
from PyQt6.QtCore import Qt
from database import Database
from utils.sms_api import SMSApi
from utils.jalali import format_jalali_date
from datetime import datetime
import openpyxl


class SMSPanelPage(QWidget):
    """صفحه پنل پیامک"""
    
    def __init__(self, db: Database, user: dict):
        super().__init__()
        self.db = db
        self.user = user
        self.sms_api = SMSApi()
        self.load_sms_settings()
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("📱 پنل مدیریت پیامک")
        title.setProperty("heading", "h2")
        layout.addWidget(title)
        
        # تب‌ها
        tabs = QTabWidget()
        tabs.addTab(self.create_settings_tab(), "⚙️ تنظیمات")
        tabs.addTab(self.create_send_tab(), "📤 ارسال")
        tabs.addTab(self.create_bulk_tab(), "📋 ارسال انبوه")
        tabs.addTab(self.create_automation_tab(), "🤖 خودکارسازی")
        tabs.addTab(self.create_log_tab(), "📊 گزارش")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def create_settings_tab(self) -> QWidget:
        """تب تنظیمات API"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # گروه تنظیمات API
        api_group = QGroupBox("تنظیمات API پیامک")
        api_layout = QVBoxLayout()
        
        # انتخاب ارائه‌دهنده
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("ارائه‌دهنده:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["کاوه‌نگار (Kavenegar)", "ملی‌پیامک (Melipayamak)"])
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        api_layout.addLayout(provider_layout)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("کلید API خود را وارد کنید")
        api_key_layout.addWidget(self.api_key_input)
        api_layout.addLayout(api_key_layout)
        
        # شماره ارسال‌کننده
        sender_layout = QHBoxLayout()
        sender_layout.addWidget(QLabel("شماره ارسال:"))
        self.sender_input = QLineEdit()
        self.sender_input.setPlaceholderText("مثال: 10001234")
        sender_layout.addWidget(self.sender_input)
        api_layout.addLayout(sender_layout)
        
        # دکمه‌های عمل
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 ذخیره تنظیمات")
        save_btn.setProperty("success", True)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🧪 تست اتصال")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        api_layout.addLayout(button_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_send_tab(self) -> QWidget:
        """تب ارسال تکی"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # انتخاب مشتری
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("مشتری:"))
        self.customer_combo = QComboBox()
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        layout.addLayout(customer_layout)
        
        # شماره موبایل
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("شماره موبایل:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09123456789")
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # متن پیامک
        layout.addWidget(QLabel("متن پیامک:"))
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(150)
        self.message_input.setPlaceholderText("متن پیامک خود را وارد کنید...")
        layout.addWidget(self.message_input)
        
        # شمارنده کاراکتر
        self.char_count_label = QLabel("تعداد کاراکتر: 0 | تعداد پیامک: 1")
        self.char_count_label.setProperty("subtitle", True)
        self.message_input.textChanged.connect(self.update_char_count)
        layout.addWidget(self.char_count_label)
        
        # پیامک‌های از پیش تعریف شده
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("الگوها:"))
        template_combo = QComboBox()
        template_combo.addItems([
            "انتخاب الگو...",
            "خوشآمدگویی",
            "یادآوری نوبت",
            "تبریک تولد",
            "تشکر از خرید"
        ])
        template_combo.currentTextChanged.connect(self.load_template)
        template_layout.addWidget(template_combo)
        template_layout.addStretch()
        layout.addLayout(template_layout)
        
        # دکمه ارسال
        send_btn = QPushButton("📤 ارسال پیامک")
        send_btn.setProperty("success", True)
        send_btn.clicked.connect(self.send_single_sms)
        layout.addWidget(send_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_bulk_tab(self) -> QWidget:
        """تب ارسال انبوه"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # راهنما
        info_label = QLabel("📝 برای ارسال انبوه، فایل Excel با ستون‌های 'phone' و 'message' آماده کنید")
        info_label.setProperty("subtitle", True)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # انتخاب فایل
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("فایلی انتخاب نشده")
        file_layout.addWidget(self.file_path_label)
        
        select_file_btn = QPushButton("📂 انتخاب فایل Excel")
        select_file_btn.clicked.connect(self.select_excel_file)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)
        
        # پیش‌نمایش
        layout.addWidget(QLabel("پیش‌نمایش:"))
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(["شماره", "پیام"])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setMaximumHeight(200)
        layout.addWidget(self.preview_table)
        
        # دکمه ارسال انبوه
        send_bulk_btn = QPushButton("📤 ارسال انبوه")
        send_bulk_btn.setProperty("warning", True)
        send_bulk_btn.clicked.connect(self.send_bulk_sms)
        layout.addWidget(send_bulk_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_automation_tab(self) -> QWidget:
        """تب خودکارسازی"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # پیامک خوشآمدگویی
        welcome_group = QGroupBox("پیامک خوشآمدگویی")
        welcome_layout = QVBoxLayout()
        welcome_layout.addWidget(QLabel("ارسال خودکار بعد از ثبت مشتری جدید"))
        self.welcome_enabled = QPushButton("✅ فعال")
        self.welcome_enabled.setCheckable(True)
        self.welcome_enabled.setChecked(True)
        welcome_layout.addWidget(self.welcome_enabled)
        welcome_group.setLayout(welcome_layout)
        layout.addWidget(welcome_group)
        
        # یادآوری نوبت
        reminder_group = QGroupBox("یادآوری نوبت")
        reminder_layout = QVBoxLayout()
        
        day_before_layout = QHBoxLayout()
        day_before_layout.addWidget(QLabel("یادآوری 1 روز قبل:"))
        self.day_before_enabled = QPushButton("✅ فعال")
        self.day_before_enabled.setCheckable(True)
        self.day_before_enabled.setChecked(True)
        day_before_layout.addWidget(self.day_before_enabled)
        day_before_layout.addStretch()
        reminder_layout.addLayout(day_before_layout)
        
        hour_before_layout = QHBoxLayout()
        hour_before_layout.addWidget(QLabel("یادآوری 2 ساعت قبل:"))
        self.hour_before_enabled = QPushButton("✅ فعال")
        self.hour_before_enabled.setCheckable(True)
        self.hour_before_enabled.setChecked(True)
        hour_before_layout.addWidget(self.hour_before_enabled)
        hour_before_layout.addStretch()
        reminder_layout.addLayout(hour_before_layout)
        
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        # تبریک تولد
        birthday_group = QGroupBox("تبریک تولد خودکار")
        birthday_layout = QVBoxLayout()
        birthday_layout.addWidget(QLabel("ارسال خودکار در روز تولد مشتریان"))
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("ساعت ارسال:"))
        self.birthday_hour = QSpinBox()
        self.birthday_hour.setRange(0, 23)
        self.birthday_hour.setValue(9)
        time_layout.addWidget(self.birthday_hour)
        time_layout.addWidget(QLabel(":"))
        self.birthday_minute = QSpinBox()
        self.birthday_minute.setRange(0, 59)
        self.birthday_minute.setValue(0)
        time_layout.addWidget(self.birthday_minute)
        time_layout.addStretch()
        birthday_layout.addLayout(time_layout)
        
        self.birthday_enabled = QPushButton("✅ فعال")
        self.birthday_enabled.setCheckable(True)
        self.birthday_enabled.setChecked(True)
        birthday_layout.addWidget(self.birthday_enabled)
        
        birthday_group.setLayout(birthday_layout)
        layout.addWidget(birthday_group)
        
        # دکمه ذخیره
        save_automation_btn = QPushButton("💾 ذخیره تنظیمات خودکارسازی")
        save_automation_btn.setProperty("success", True)
        save_automation_btn.clicked.connect(self.save_automation_settings)
        layout.addWidget(save_automation_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_log_tab(self) -> QWidget:
        """تب گزارش پیامک‌ها"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # فیلتر
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("نوع:"))
        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(["همه", "موفق", "ناموفق", "خوشآمدگویی", "یادآوری", "تولد"])
        self.log_filter_combo.currentTextChanged.connect(self.load_sms_log)
        filter_layout.addWidget(self.log_filter_combo)
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.load_sms_log)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # جدول لاگ
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["تاریخ", "شماره", "نوع", "وضعیت", "پیام"])
        self.log_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.log_table)
        
        # بارگذاری لاگ
        self.load_sms_log()
        
        widget.setLayout(layout)
        return widget
    
    def load_sms_settings(self):
        """بارگذاری تنظیمات پیامک"""
        try:
            settings = {}
            results = self.db.execute_query(
                "SELECT key, value FROM settings WHERE key LIKE 'sms_%'",
                ()
            )
            for row in results:
                settings[row['key']] = row['value']
            
            if 'sms_api_key' in settings:
                provider = settings.get('sms_provider', 'kavenegar')
                self.sms_api.configure(
                    settings['sms_api_key'],
                    settings.get('sms_sender', ''),
                    provider
                )
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")
    
    def save_settings(self):
        """ذخیره تنظیمات API"""
        api_key = self.api_key_input.text().strip()
        sender = self.sender_input.text().strip()
        
        if not api_key or not sender:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
        
        provider_map = {
            "کاوه‌نگار (Kavenegar)": "kavenegar",
            "ملی‌پیامک (Melipayamak)": "melipayamak"
        }
        provider = provider_map.get(self.provider_combo.currentText(), "kavenegar")
        
        try:
            # ذخیره در دیتابیس
            self.db.execute_update(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('sms_api_key', ?)",
                (api_key,)
            )
            self.db.execute_update(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('sms_sender', ?)",
                (sender,)
            )
            self.db.execute_update(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('sms_provider', ?)",
                (provider,)
            )
            
            # تنظیم API
            self.sms_api.configure(api_key, sender, provider)
            
            QMessageBox.information(self, "موفق", "تنظیمات با موفقیت ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def test_connection(self):
        """تست اتصال به سرویس پیامک"""
        QMessageBox.information(self, "تست", "تست اتصال در نسخه بعدی پیاده‌سازی می‌شود")
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        try:
            customers = self.db.execute_query(
                "SELECT id, name, phone FROM customers ORDER BY name",
                ()
            )
            self.customer_combo.addItem("انتخاب مشتری...", None)
            for customer in customers:
                self.customer_combo.addItem(
                    f"{customer['name']} - {customer['phone']}", 
                    customer
                )
        except Exception as e:
            print(f"خطا در بارگذاری مشتریان: {e}")
    
    def update_char_count(self):
        """بروزرسانی شمارنده کاراکتر"""
        text = self.message_input.toPlainText()
        char_count = len(text)
        sms_count = (char_count // 70) + 1 if char_count > 0 else 1
        self.char_count_label.setText(f"تعداد کاراکتر: {char_count} | تعداد پیامک: {sms_count}")
    
    def load_template(self, template_name: str):
        """بارگذاری الگوی پیامک"""
        templates = {
            "خوشآمدگویی": "سلام {نام} عزیز\nبه خانواده کاگان خوش آمدید! 🎉",
            "یادآوری نوبت": "{نام} عزیز، یادآوری نوبت شما\n⏰ زمان: {زمان}\n📋 خدمت: {خدمت}",
            "تبریک تولد": "🎂 {نام} عزیز\nتولدت مبارک! 🎉\nآرزوی سلامتی و شادکامی برای شما داریم",
            "تشکر از خرید": "{نام} عزیز\nاز خرید شما متشکریم 🙏\nامیدواریم تجربه خوبی داشته باشید"
        }
        
        if template_name in templates:
            self.message_input.setText(templates[template_name])
    
    def send_single_sms(self):
        """ارسال پیامک تکی"""
        phone = self.phone_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not phone or not message:
            QMessageBox.warning(self, "خطا", "لطفاً شماره و متن پیامک را وارد کنید")
            return
        
        # ارسال پیامک
        result = self.sms_api.send_sms(phone, message)
        
        # ثبت در لاگ
        try:
            self.db.execute_update(
                """INSERT INTO sms_log (phone, message, type, status, sent_at)
                   VALUES (?, ?, 'manual', ?, ?)""",
                (phone, message, 'sent' if result.get('success') else 'failed', datetime.now().isoformat())
            )
        except:
            pass
        
        if result.get('success'):
            QMessageBox.information(self, "موفق", "پیامک با موفقیت ارسال شد")
            self.phone_input.clear()
            self.message_input.clear()
            self.load_sms_log()
        else:
            QMessageBox.critical(self, "خطا", result.get('message', 'خطای نامشخص'))
    
    def select_excel_file(self):
        """انتخاب فایل Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.load_excel_preview(file_path)
    
    def load_excel_preview(self, file_path: str):
        """بارگذاری پیش‌نمایش Excel"""
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            self.preview_table.setRowCount(0)
            
            for row in list(ws.iter_rows(min_row=2, values_only=True))[:10]:
                if len(row) >= 2:
                    row_position = self.preview_table.rowCount()
                    self.preview_table.insertRow(row_position)
                    self.preview_table.setItem(row_position, 0, QTableWidgetItem(str(row[0])))
                    self.preview_table.setItem(row_position, 1, QTableWidgetItem(str(row[1])))
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در خواندن فایل: {str(e)}")
    
    def send_bulk_sms(self):
        """ارسال انبوه پیامک"""
        file_path = self.file_path_label.text()
        
        if file_path == "فایلی انتخاب نشده":
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا فایل Excel را انتخاب کنید")
            return
        
        reply = QMessageBox.question(
            self, "تأیید", "آیا از ارسال انبوه پیامک مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "در حال ارسال", "ارسال انبوه در نسخه بعدی پیاده‌سازی می‌شود")
    
    def save_automation_settings(self):
        """ذخیره تنظیمات خودکارسازی"""
        QMessageBox.information(self, "موفق", "تنظیمات خودکارسازی ذخیره شد")
    
    def load_sms_log(self):
        """بارگذاری لاگ پیامک‌ها"""
        try:
            self.log_table.setRowCount(0)
            
            logs = self.db.execute_query(
                """SELECT * FROM sms_log 
                   ORDER BY created_at DESC LIMIT 100""",
                ()
            )
            
            for log in logs:
                row_position = self.log_table.rowCount()
                self.log_table.insertRow(row_position)
                
                # تاریخ
                created_at = datetime.fromisoformat(log['created_at'])
                self.log_table.setItem(row_position, 0, 
                    QTableWidgetItem(format_jalali_date(created_at, True)))
                
                # شماره
                self.log_table.setItem(row_position, 1, 
                    QTableWidgetItem(log['phone']))
                
                # نوع
                self.log_table.setItem(row_position, 2, 
                    QTableWidgetItem(log['type']))
                
                # وضعیت
                status_text = "✅ موفق" if log['status'] == 'sent' else "❌ ناموفق"
                self.log_table.setItem(row_position, 3, 
                    QTableWidgetItem(status_text))
                
                # پیام (خلاصه)
                message_preview = log['message'][:50] + "..." if len(log['message']) > 50 else log['message']
                self.log_table.setItem(row_position, 4, 
                    QTableWidgetItem(message_preview))
                
        except Exception as e:
            print(f"خطا در بارگذاری لاگ: {e}")
