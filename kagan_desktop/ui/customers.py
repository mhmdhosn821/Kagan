"""
صفحه مدیریت مشتریان (CRM)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QDateEdit, QTextEdit, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


class CustomersPage(QWidget):
    """صفحه مدیریت مشتریان"""
    
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
        
        # جستجو
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس نام یا تلفن...")
        self.search_input.textChanged.connect(self.load_customers)
        toolbar.addWidget(self.search_input)
        
        # دکمه افزودن
        add_btn = QPushButton("➕ افزودن مشتری")
        add_btn.clicked.connect(self.add_customer)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول مشتریان
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "شناسه", "نام", "تلفن", "ایمیل", "امتیاز وفاداری", "تاریخ ثبت", "عملیات"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.customers_table)
        
        self.setLayout(layout)
        self.load_customers()
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        search = self.search_input.text().strip()
        
        if search:
            query = """
                SELECT id, name, phone, email, loyalty_points, created_at
                FROM customers
                WHERE name LIKE ? OR phone LIKE ?
                ORDER BY created_at DESC
            """
            customers = self.db.execute_query(query, (f"%{search}%", f"%{search}%"))
        else:
            query = """
                SELECT id, name, phone, email, loyalty_points, created_at
                FROM customers
                ORDER BY created_at DESC
            """
            customers = self.db.execute_query(query)
        
        self.customers_table.setRowCount(len(customers))
        
        for i, customer in enumerate(customers):
            self.customers_table.setItem(i, 0, QTableWidgetItem(str(customer['id'])))
            self.customers_table.setItem(i, 1, QTableWidgetItem(customer['name']))
            self.customers_table.setItem(i, 2, QTableWidgetItem(customer['phone'] or "-"))
            self.customers_table.setItem(i, 3, QTableWidgetItem(customer['email'] or "-"))
            self.customers_table.setItem(i, 4, QTableWidgetItem(str(customer['loyalty_points'])))
            
            # فرمت تاریخ
            created_at = customer['created_at']
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at)
                    date_str = dt.strftime("%Y/%m/%d")
                except:
                    date_str = created_at
            else:
                date_str = "-"
            self.customers_table.setItem(i, 5, QTableWidgetItem(date_str))
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, cid=customer['id']: self.edit_customer(cid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, cid=customer['id']: self.delete_customer(cid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.customers_table.setCellWidget(i, 6, actions_widget)
    
    def add_customer(self):
        """افزودن مشتری جدید"""
        dialog = CustomerDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def edit_customer(self, customer_id: int):
        """ویرایش مشتری"""
        dialog = CustomerDialog(self.db, customer_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def delete_customer(self, customer_id: int):
        """حذف مشتری"""
        reply = QMessageBox.question(
            self,
            "حذف مشتری",
            "آیا مطمئن هستید که می‌خواهید این مشتری را حذف کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute_update("DELETE FROM customers WHERE id = ?", (customer_id,))
                QMessageBox.information(self, "موفق", "مشتری با موفقیت حذف شد.")
                self.load_customers()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف مشتری: {str(e)}")


class CustomerDialog(QDialog):
    """دیالوگ افزودن/ویرایش مشتری"""
    
    def __init__(self, db, customer_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.customer_id = customer_id
        self.init_ui()
        
        if customer_id:
            self.load_customer()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن مشتری" if not self.customer_id else "ویرایش مشتری")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # نام
        self.name_input = QLineEdit()
        layout.addRow("نام:", self.name_input)
        
        # تلفن
        self.phone_input = QLineEdit()
        layout.addRow("تلفن:", self.phone_input)
        
        # ایمیل
        self.email_input = QLineEdit()
        layout.addRow("ایمیل:", self.email_input)
        
        # تاریخ تولد
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())
        layout.addRow("تاریخ تولد:", self.birth_date_input)
        
        # امتیاز وفاداری
        self.loyalty_input = QSpinBox()
        self.loyalty_input.setMaximum(1000000)
        layout.addRow("امتیاز وفاداری:", self.loyalty_input)
        
        # یادداشت
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        layout.addRow("یادداشت:", self.notes_input)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
    
    def load_customer(self):
        """بارگذاری اطلاعات مشتری"""
        query = "SELECT * FROM customers WHERE id = ?"
        result = self.db.execute_query(query, (self.customer_id,))
        
        if result:
            customer = result[0]
            self.name_input.setText(customer['name'])
            self.phone_input.setText(customer['phone'] or "")
            self.email_input.setText(customer['email'] or "")
            
            if customer['birth_date']:
                try:
                    date = QDate.fromString(customer['birth_date'], "yyyy-MM-dd")
                    self.birth_date_input.setDate(date)
                except:
                    pass
            
            self.loyalty_input.setValue(customer['loyalty_points'])
            self.notes_input.setPlainText(customer['notes'] or "")
    
    def save(self):
        """ذخیره مشتری"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "خطا", "نام مشتری الزامی است.")
            return
        
        phone = self.phone_input.text().strip() or None
        email = self.email_input.text().strip() or None
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        loyalty_points = self.loyalty_input.value()
        notes = self.notes_input.toPlainText().strip() or None
        
        try:
            if self.customer_id:
                # ویرایش
                query = """
                    UPDATE customers 
                    SET name = ?, phone = ?, email = ?, birth_date = ?, 
                        loyalty_points = ?, notes = ?
                    WHERE id = ?
                """
                self.db.execute_update(query, (name, phone, email, birth_date, loyalty_points, notes, self.customer_id))
                QMessageBox.information(self, "موفق", "مشتری با موفقیت ویرایش شد.")
            else:
                # افزودن
                query = """
                    INSERT INTO customers (name, phone, email, birth_date, loyalty_points, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                self.db.execute_update(query, (name, phone, email, birth_date, loyalty_points, notes))
                QMessageBox.information(self, "موفق", "مشتری با موفقیت افزوده شد.")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره مشتری: {str(e)}")
