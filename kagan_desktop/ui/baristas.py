"""
صفحه مدیریت باریستاها
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt


class BaristasPage(QWidget):
    """صفحه مدیریت باریستاها"""
    
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
        self.search_input.setPlaceholderText("🔍 جستجو باریستاها...")
        self.search_input.textChanged.connect(self.load_baristas)
        toolbar.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ افزودن باریستا")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_barista)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول باریستاها
        self.baristas_table = QTableWidget()
        self.baristas_table.setColumnCount(5)
        self.baristas_table.setHorizontalHeaderLabels([
            "نام", "شماره تماس", "شیفت کاری", "وضعیت", "عملیات"
        ])
        self.baristas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.baristas_table.setAlternatingRowColors(True)
        self.baristas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.baristas_table)
        
        self.setLayout(layout)
        self.load_baristas()
    
    def load_baristas(self):
        """بارگذاری لیست باریستاها"""
        search = self.search_input.text().strip()
        
        if search:
            query = """
                SELECT * FROM users 
                WHERE role = 'barista' AND (full_name LIKE ? OR phone LIKE ?)
                ORDER BY full_name
            """
            baristas = self.db.execute_query(query, (f"%{search}%", f"%{search}%"))
        else:
            query = "SELECT * FROM users WHERE role = 'barista' ORDER BY full_name"
            baristas = self.db.execute_query(query)
        
        self.baristas_table.setRowCount(len(baristas))
        
        for i, barista in enumerate(baristas):
            self.baristas_table.setItem(i, 0, QTableWidgetItem(barista['full_name']))
            self.baristas_table.setItem(i, 1, QTableWidgetItem(barista['phone'] or "-"))
            self.baristas_table.setItem(i, 2, QTableWidgetItem(barista['shift'] or "-"))
            
            status = "فعال" if barista['is_active'] else "غیرفعال"
            status_item = QTableWidgetItem(status)
            self.baristas_table.setItem(i, 3, status_item)
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("✏️ ویرایش")
            edit_btn.clicked.connect(lambda checked, bid=barista['id']: self.edit_barista(bid))
            actions_layout.addWidget(edit_btn)
            
            toggle_btn = QPushButton("🔄 تغییر وضعیت")
            toggle_btn.clicked.connect(lambda checked, bid=barista['id']: self.toggle_status(bid))
            actions_layout.addWidget(toggle_btn)
            
            actions_widget.setLayout(actions_layout)
            self.baristas_table.setCellWidget(i, 4, actions_widget)
    
    def add_barista(self):
        """افزودن باریستا جدید"""
        dialog = BaristaDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_baristas()
    
    def edit_barista(self, barista_id: int):
        """ویرایش باریستا"""
        dialog = BaristaDialog(self.db, barista_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_baristas()
    
    def toggle_status(self, barista_id: int):
        """تغییر وضعیت باریستا"""
        query = "SELECT is_active FROM users WHERE id = ?"
        result = self.db.execute_query(query, (barista_id,))
        if result:
            current_status = result[0]['is_active']
            new_status = 0 if current_status else 1
            
            query = "UPDATE users SET is_active = ? WHERE id = ?"
            self.db.execute_update(query, (new_status, barista_id))
            
            QMessageBox.information(self, "موفق", "وضعیت باریستا تغییر یافت.")
            self.load_baristas()


class BaristaDialog(QDialog):
    """دیالوگ افزودن/ویرایش باریستا"""
    
    def __init__(self, db, barista_id: int = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.barista_id = barista_id
        self.init_ui()
        
        if barista_id:
            self.load_barista()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن باریستا" if not self.barista_id else "ویرایش باریستا")
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        # نام
        self.name_input = QLineEdit()
        layout.addRow("نام کامل:", self.name_input)
        
        # نام کاربری
        self.username_input = QLineEdit()
        self.username_input.setEnabled(not self.barista_id)  # فقط در افزودن
        layout.addRow("نام کاربری:", self.username_input)
        
        # رمز عبور
        if not self.barista_id:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addRow("رمز عبور:", self.password_input)
        
        # شماره تماس
        self.phone_input = QLineEdit()
        layout.addRow("شماره تماس:", self.phone_input)
        
        # شیفت کاری
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["صبح", "عصر", "شب", "تمام وقت"])
        layout.addRow("شیفت کاری:", self.shift_combo)
        
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
    
    def load_barista(self):
        """بارگذاری اطلاعات باریستا"""
        query = "SELECT * FROM users WHERE id = ?"
        result = self.db.execute_query(query, (self.barista_id,))
        
        if result:
            barista = result[0]
            self.name_input.setText(barista['full_name'])
            self.username_input.setText(barista['username'])
            self.phone_input.setText(barista['phone'] or "")
            if barista['shift']:
                index = self.shift_combo.findText(barista['shift'])
                if index >= 0:
                    self.shift_combo.setCurrentIndex(index)
            self.active_checkbox.setChecked(barista['is_active'] == 1)
    
    def save(self):
        """ذخیره اطلاعات"""
        import hashlib
        
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        phone = self.phone_input.text().strip()
        shift = self.shift_combo.currentText()
        is_active = 1 if self.active_checkbox.isChecked() else 0
        
        if not name or not username:
            QMessageBox.warning(self, "خطا", "لطفاً نام و نام کاربری را وارد کنید.")
            return
        
        if not self.barista_id:
            # افزودن جدید
            password = self.password_input.text().strip()
            if not password:
                QMessageBox.warning(self, "خطا", "لطفاً رمز عبور را وارد کنید.")
                return
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            query = """
                INSERT INTO users (username, password, full_name, role, phone, shift, is_active)
                VALUES (?, ?, ?, 'barista', ?, ?, ?)
            """
            try:
                self.db.execute_update(query, (username, password_hash, name, phone, shift, is_active))
                QMessageBox.information(self, "موفق", "باریستا با موفقیت اضافه شد.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن باریستا: {str(e)}")
        else:
            # ویرایش
            query = """
                UPDATE users 
                SET full_name = ?, phone = ?, shift = ?, is_active = ?
                WHERE id = ?
            """
            try:
                self.db.execute_update(query, (name, phone, shift, is_active, self.barista_id))
                QMessageBox.information(self, "موفق", "اطلاعات باریستا با موفقیت بروزرسانی شد.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بروزرسانی: {str(e)}")
