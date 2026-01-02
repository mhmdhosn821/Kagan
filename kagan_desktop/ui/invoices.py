"""
صفحه فاکتورزنی
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QSpinBox
)
from datetime import datetime
import random


class InvoicesPage(QWidget):
    """صفحه فاکتورزنی"""
    
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
        
        new_invoice_btn = QPushButton("➕ فاکتور جدید")
        new_invoice_btn.clicked.connect(self.create_invoice)
        toolbar.addWidget(new_invoice_btn)
        
        toolbar.addStretch()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.load_invoices)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # جدول فاکتورها
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            "شماره", "نوع", "مشتری", "مبلغ کل", "تخفیف", "روش پرداخت", "تاریخ"
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.invoices_table)
        self.setLayout(layout)
        self.load_invoices()
    
    def load_invoices(self):
        """بارگذاری لیست فاکتورها"""
        query = """
            SELECT i.invoice_number, i.invoice_type, c.name as customer_name,
                   i.total_amount, i.discount_amount, i.payment_method, i.created_at
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT 100
        """
        invoices = self.db.execute_query(query)
        
        self.invoices_table.setRowCount(len(invoices))
        
        invoice_types = {
            "cafe": "کافه",
            "barbershop": "آرایشگاه",
            "mixed": "ترکیبی"
        }
        
        payment_methods = {
            "cash": "نقدی",
            "card": "کارت",
            "credit": "اعتباری"
        }
        
        for i, invoice in enumerate(invoices):
            self.invoices_table.setItem(i, 0, QTableWidgetItem(invoice['invoice_number']))
            self.invoices_table.setItem(i, 1, QTableWidgetItem(invoice_types.get(invoice['invoice_type'], invoice['invoice_type'])))
            self.invoices_table.setItem(i, 2, QTableWidgetItem(invoice['customer_name'] or "مشتری عمومی"))
            self.invoices_table.setItem(i, 3, QTableWidgetItem(f"{invoice['total_amount']:,.0f} ریال"))
            self.invoices_table.setItem(i, 4, QTableWidgetItem(f"{invoice['discount_amount']:,.0f} ریال"))
            self.invoices_table.setItem(i, 5, QTableWidgetItem(payment_methods.get(invoice['payment_method'], invoice['payment_method'])))
            
            try:
                dt = datetime.fromisoformat(invoice['created_at'])
                date_str = dt.strftime("%Y/%m/%d %H:%M")
            except:
                date_str = invoice['created_at']
            self.invoices_table.setItem(i, 6, QTableWidgetItem(date_str))
    
    def create_invoice(self):
        """ایجاد فاکتور جدید"""
        dialog = InvoiceDialog(self.db, self.user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_invoices()


class InvoiceDialog(QDialog):
    """دیالوگ ایجاد فاکتور"""
    
    def __init__(self, db, user, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.items = []
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("فاکتور جدید")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # فرم اطلاعات فاکتور
        form_layout = QFormLayout()
        
        # مشتری
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("مشتری عمومی", None)
        self.load_customers()
        form_layout.addRow("مشتری:", self.customer_combo)
        
        # نوع فاکتور
        self.invoice_type_combo = QComboBox()
        if self.user['role'] == 'admin':
            self.invoice_type_combo.addItems(["کافه", "آرایشگاه", "ترکیبی"])
        elif self.user['role'] == 'barber':
            self.invoice_type_combo.addItems(["آرایشگاه"])
        else:
            self.invoice_type_combo.addItems(["کافه"])
        self.invoice_type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("نوع:", self.invoice_type_combo)
        
        # آیتم
        self.item_combo = QComboBox()
        form_layout.addRow("آیتم:", self.item_combo)
        
        # تعداد
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(100)
        self.quantity_input.setValue(1)
        form_layout.addRow("تعداد:", self.quantity_input)
        
        # دکمه افزودن آیتم
        add_item_btn = QPushButton("➕ افزودن به فاکتور")
        add_item_btn.clicked.connect(self.add_item)
        form_layout.addRow(add_item_btn)
        
        layout.addLayout(form_layout)
        
        # جدول آیتم‌ها
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "نام", "تعداد", "قیمت واحد", "جمع", "عملیات"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.items_table)
        
        # اطلاعات مالی
        financial_layout = QFormLayout()
        
        self.subtotal_label = QLabel("0 ریال")
        financial_layout.addRow("جمع:", self.subtotal_label)
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(1000000000)
        self.discount_input.valueChanged.connect(self.update_total)
        financial_layout.addRow("تخفیف:", self.discount_input)
        
        self.total_label = QLabel("0 ریال")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        financial_layout.addRow("مبلغ نهایی:", self.total_label)
        
        # روش پرداخت
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["نقدی", "کارت", "اعتباری"])
        financial_layout.addRow("روش پرداخت:", self.payment_method_combo)
        
        layout.addLayout(financial_layout)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("ثبت فاکتور")
        save_btn.clicked.connect(self.save_invoice)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.on_type_changed()
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        query = "SELECT id, name FROM customers ORDER BY name"
        customers = self.db.execute_query(query)
        
        for customer in customers:
            self.customer_combo.addItem(customer['name'], customer['id'])
    
    def on_type_changed(self):
        """تغییر نوع فاکتور"""
        self.item_combo.clear()
        invoice_type = self.invoice_type_combo.currentText()
        
        if invoice_type == "کافه":
            query = "SELECT id, name, price FROM products ORDER BY name"
            items = self.db.execute_query(query)
            for item in items:
                self.item_combo.addItem(f"{item['name']} - {item['price']:,.0f} ریال", ('product', item['id'], item['price']))
        elif invoice_type == "آرایشگاه":
            query = "SELECT id, name, price FROM services ORDER BY name"
            items = self.db.execute_query(query)
            for item in items:
                self.item_combo.addItem(f"{item['name']} - {item['price']:,.0f} ریال", ('service', item['id'], item['price']))
        else:  # ترکیبی
            query = "SELECT id, name, price FROM products ORDER BY name"
            products = self.db.execute_query(query)
            for item in products:
                self.item_combo.addItem(f"[کافه] {item['name']} - {item['price']:,.0f} ریال", ('product', item['id'], item['price']))
            
            query = "SELECT id, name, price FROM services ORDER BY name"
            services = self.db.execute_query(query)
            for item in services:
                self.item_combo.addItem(f"[آرایشگاه] {item['name']} - {item['price']:,.0f} ریال", ('service', item['id'], item['price']))
    
    def add_item(self):
        """افزودن آیتم به فاکتور"""
        if self.item_combo.count() == 0:
            QMessageBox.warning(self, "خطا", "آیتمی برای افزودن وجود ندارد.")
            return
        
        item_data = self.item_combo.currentData()
        item_type, item_id, price = item_data
        name = self.item_combo.currentText().split(' - ')[0]
        quantity = self.quantity_input.value()
        total = price * quantity
        
        self.items.append({
            'type': item_type,
            'id': item_id,
            'name': name,
            'quantity': quantity,
            'price': price,
            'total': total
        })
        
        self.update_items_table()
        self.update_total()
    
    def update_items_table(self):
        """بروزرسانی جدول آیتم‌ها"""
        self.items_table.setRowCount(len(self.items))
        
        for i, item in enumerate(self.items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"{item['price']:,.0f}"))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{item['total']:,.0f}"))
            
            # دکمه حذف
            remove_btn = QPushButton("🗑️")
            remove_btn.setMaximumWidth(30)
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.items_table.setCellWidget(i, 4, remove_btn)
    
    def remove_item(self, index: int):
        """حذف آیتم از فاکتور"""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.update_items_table()
            self.update_total()
    
    def update_total(self):
        """بروزرسانی مبالغ"""
        subtotal = sum(item['total'] for item in self.items)
        discount = self.discount_input.value()
        total = subtotal - discount
        
        self.subtotal_label.setText(f"{subtotal:,.0f} ریال")
        self.total_label.setText(f"{total:,.0f} ریال")
    
    def save_invoice(self):
        """ثبت فاکتور"""
        if not self.items:
            QMessageBox.warning(self, "خطا", "لطفاً حداقل یک آیتم به فاکتور اضافه کنید.")
            return
        
        customer_id = self.customer_combo.currentData()
        
        invoice_types = {"کافه": "cafe", "آرایشگاه": "barbershop", "ترکیبی": "mixed"}
        invoice_type = invoice_types[self.invoice_type_combo.currentText()]
        
        subtotal = sum(item['total'] for item in self.items)
        discount = self.discount_input.value()
        total = subtotal - discount
        
        payment_methods = {"نقدی": "cash", "کارت": "card", "اعتباری": "credit"}
        payment_method = payment_methods[self.payment_method_combo.currentText()]
        
        # تولید شماره فاکتور
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        try:
            # ثبت فاکتور
            query = """
                INSERT INTO invoices (invoice_number, customer_id, user_id, invoice_type,
                                     subtotal, discount_amount, total_amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            invoice_id = self.db.execute_update(
                query,
                (invoice_number, customer_id, self.user['id'], invoice_type, subtotal, discount, total, payment_method)
            )
            
            # ثبت آیتم‌های فاکتور
            for item in self.items:
                query = """
                    INSERT INTO invoice_items (invoice_id, item_type, item_id, item_name,
                                              quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute_update(
                    query,
                    (invoice_id, item['type'], item['id'], item['name'], item['quantity'], item['price'], item['total'])
                )
            
            QMessageBox.information(self, "موفق", f"فاکتور {invoice_number} با موفقیت ثبت شد.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت فاکتور: {str(e)}")
