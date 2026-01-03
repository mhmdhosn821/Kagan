"""
صفحه مدیریت آرایشگران
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt


class BarbersPage(QWidget):
    """صفحه مدیریت آرایشگران"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 جستجو آرایشگران...")
        self.search_input.textChanged.connect(self.load_barbers)
        toolbar.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ افزودن آرایشگر")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_barber)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول آرایشگران
        self.barbers_table = QTableWidget()
        self.barbers_table.setColumnCount(6)
        self.barbers_table.setHorizontalHeaderLabels([
            "نام", "شماره تماس", "تخصص", "کمیسیون (%)", "وضعیت", "عملیات"
        ])
        self.barbers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.barbers_table.setAlternatingRowColors(True)
        self.barbers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.barbers_table)
        
        self.setLayout(layout)
        self.load_barbers()
    
    def load_barbers(self):
        """بارگذاری لیست آرایشگران"""
        search = self.search_input.text().strip()
        
        if search:
            query = """
                SELECT * FROM users 
                WHERE role = 'barber' AND (full_name LIKE ? OR phone LIKE ?)
                ORDER BY full_name
            """
            barbers = self.db.execute_query(query, (f"%{search}%", f"%{search}%"))
        else:
            query = "SELECT * FROM users WHERE role = 'barber' ORDER BY full_name"
            barbers = self.db.execute_query(query)
        
        self.barbers_table.setRowCount(len(barbers))
        
        for i, barber in enumerate(barbers):
            barber_dict = dict(barber)
            self.barbers_table.setItem(i, 0, QTableWidgetItem(barber_dict.get('full_name', '')))
            self.barbers_table.setItem(i, 1, QTableWidgetItem(barber_dict.get('phone') or "-"))
            self.barbers_table.setItem(i, 2, QTableWidgetItem(barber_dict.get('specialty') or "-"))
            self.barbers_table.setItem(i, 3, QTableWidgetItem(f"{barber_dict.get('commission_percentage', 0)}%"))
            
            status = "فعال" if barber_dict.get('is_active') else "غیرفعال"
            status_item = QTableWidgetItem(status)
            self.barbers_table.setItem(i, 4, status_item)
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("✏️ ویرایش")
            edit_btn.clicked.connect(lambda checked, bid=barber_dict.get('id'): self.edit_barber(bid))
            actions_layout.addWidget(edit_btn)
            
            toggle_btn = QPushButton("🔄 تغییر وضعیت")
            toggle_btn.clicked.connect(lambda checked, bid=barber_dict.get('id'): self.toggle_status(bid))
            actions_layout.addWidget(toggle_btn)
            
            actions_widget.setLayout(actions_layout)
            self.barbers_table.setCellWidget(i, 5, actions_widget)
    
    def add_barber(self):
        """افزودن آرایشگر جدید"""
        dialog = BarberDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_barbers()
    
    def edit_barber(self, barber_id: int):
        """ویرایش آرایشگر"""
        dialog = BarberDialog(self.db, barber_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_barbers()
    
    def toggle_status(self, barber_id: int):
        """تغییر وضعیت آرایشگر"""
        query = "SELECT is_active FROM users WHERE id = ?"
        result = self.db.execute_query(query, (barber_id,))
        if result:
            current_status = result[0]['is_active']
            new_status = 0 if current_status else 1
            
            query = "UPDATE users SET is_active = ? WHERE id = ?"
            self.db.execute_update(query, (new_status, barber_id))
            
            QMessageBox.information(self, "موفق", "وضعیت آرایشگر تغییر یافت.")
            self.load_barbers()


class BarberDialog(QDialog):
    """دیالوگ افزودن/ویرایش آرایشگر"""
    
    def __init__(self, db, barber_id: int = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.barber_id = barber_id
        self.init_ui()
        
        if barber_id:
            self.load_barber()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن آرایشگر" if not self.barber_id else "ویرایش آرایشگر")
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        # نام
        self.name_input = QLineEdit()
        layout.addRow("نام کامل:", self.name_input)
        
        # نام کاربری
        self.username_input = QLineEdit()
        self.username_input.setEnabled(not self.barber_id)  # فقط در افزودن
        layout.addRow("نام کاربری:", self.username_input)
        
        # رمز عبور
        if not self.barber_id:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addRow("رمز عبور:", self.password_input)
        
        # شماره تماس
        self.phone_input = QLineEdit()
        layout.addRow("شماره تماس:", self.phone_input)
        
        # تخصص
        self.specialty_input = QLineEdit()
        self.specialty_input.setPlaceholderText("مثال: اصلاح، رنگ، گریم")
        layout.addRow("تخصص:", self.specialty_input)
        
        # درصد کمیسیون
        self.commission_input = QDoubleSpinBox()
        self.commission_input.setRange(0, 100)
        self.commission_input.setSuffix("%")
        layout.addRow("درصد کمیسیون:", self.commission_input)
        
        # وضعیت
        self.active_checkbox = QCheckBox("فعال")
        self.active_checkbox.setChecked(True)
        layout.addRow("وضعیت:", self.active_checkbox)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 ذخیره")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
    
    def load_barber(self):
        """بارگذاری اطلاعات آرایشگر"""
        query = "SELECT * FROM users WHERE id = ?"
        result = self.db.execute_query(query, (self.barber_id,))
        
        if result:
            barber = dict(result[0])
            self.name_input.setText(barber.get('full_name', ''))
            self.username_input.setText(barber.get('username', ''))
            self.phone_input.setText(barber.get('phone') or "")
            self.specialty_input.setText(barber.get('specialty') or "")
            self.commission_input.setValue(barber.get('commission_percentage', 0))
            self.active_checkbox.setChecked(barber.get('is_active', 1) == 1)
    
    def save(self):
        """ذخیره اطلاعات"""
        import hashlib
        
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        phone = self.phone_input.text().strip()
        specialty = self.specialty_input.text().strip()
        commission = self.commission_input.value()
        is_active = 1 if self.active_checkbox.isChecked() else 0
        
        if not name or not username:
            QMessageBox.warning(self, "خطا", "لطفاً نام و نام کاربری را وارد کنید.")
            return
        
        if not self.barber_id:
            # افزودن جدید
            password = self.password_input.text().strip()
            if not password:
                QMessageBox.warning(self, "خطا", "لطفاً رمز عبور را وارد کنید.")
                return
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            query = """
                INSERT INTO users (username, password, full_name, role, phone, specialty, commission_percentage, is_active)
                VALUES (?, ?, ?, 'barber', ?, ?, ?, ?)
            """
            try:
                self.db.execute_update(query, (username, password_hash, name, phone, specialty, commission, is_active))
                QMessageBox.information(self, "موفق", "آرایشگر با موفقیت اضافه شد.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن آرایشگر: {str(e)}")
        else:
            # ویرایش
            query = """
                UPDATE users 
                SET full_name = ?, phone = ?, specialty = ?, commission_percentage = ?, is_active = ?
                WHERE id = ?
            """
            try:
                self.db.execute_update(query, (name, phone, specialty, commission, is_active, self.barber_id))
                QMessageBox.information(self, "موفق", "اطلاعات آرایشگر با موفقیت بروزرسانی شد.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بروزرسانی: {str(e)}")
