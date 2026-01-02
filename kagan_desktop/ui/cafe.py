"""
صفحه بخش کافه
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QTextEdit
)


class CafePage(QWidget):
    """صفحه بخش کافه"""
    
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
        self.search_input.setPlaceholderText("جستجو محصولات...")
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ افزودن محصول")
        add_btn.clicked.connect(self.add_product)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول محصولات
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "نام", "کد", "دسته", "قیمت", "توضیحات", "عملیات"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.products_table)
        self.setLayout(layout)
        self.load_products()
    
    def load_products(self):
        """بارگذاری لیست محصولات"""
        search = self.search_input.text().strip()
        
        if search:
            query = "SELECT * FROM products WHERE name LIKE ? OR code LIKE ? ORDER BY name"
            products = self.db.execute_query(query, (f"%{search}%", f"%{search}%"))
        else:
            query = "SELECT * FROM products ORDER BY name"
            products = self.db.execute_query(query)
        
        self.products_table.setRowCount(len(products))
        
        categories = {
            "coffee": "قهوه",
            "tea": "چای",
            "chocolate": "شکلات",
            "dessert": "دسر"
        }
        
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product['name']))
            self.products_table.setItem(i, 1, QTableWidgetItem(product['code']))
            self.products_table.setItem(i, 2, QTableWidgetItem(categories.get(product['category'], product['category'])))
            self.products_table.setItem(i, 3, QTableWidgetItem(f"{product['price']:,.0f} ریال"))
            self.products_table.setItem(i, 4, QTableWidgetItem(product['description'] or "-"))
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, pid=product['id']: self.edit_product(pid))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            self.products_table.setCellWidget(i, 5, actions_widget)
    
    def add_product(self):
        """افزودن محصول جدید"""
        dialog = ProductDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def edit_product(self, product_id: int):
        """ویرایش محصول"""
        dialog = ProductDialog(self.db, product_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()


class ProductDialog(QDialog):
    """دیالوگ افزودن/ویرایش محصول"""
    
    def __init__(self, db, product_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.init_ui()
        
        if product_id:
            self.load_product()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن محصول" if not self.product_id else "ویرایش محصول")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow("نام:", self.name_input)
        
        self.code_input = QLineEdit()
        layout.addRow("کد:", self.code_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["قهوه", "چای", "شکلات", "دسر"])
        layout.addRow("دسته:", self.category_combo)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(10000000)
        self.price_input.setDecimals(0)
        layout.addRow("قیمت:", self.price_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("توضیحات:", self.description_input)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        self.setLayout(layout)
    
    def load_product(self):
        """بارگذاری اطلاعات محصول"""
        query = "SELECT * FROM products WHERE id = ?"
        result = self.db.execute_query(query, (self.product_id,))
        
        if result:
            product = result[0]
            self.name_input.setText(product['name'])
            self.code_input.setText(product['code'])
            
            categories = ["coffee", "tea", "chocolate", "dessert"]
            if product['category'] in categories:
                self.category_combo.setCurrentIndex(categories.index(product['category']))
            
            self.price_input.setValue(product['price'])
            self.description_input.setPlainText(product['description'] or "")
    
    def save(self):
        """ذخیره محصول"""
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()
        
        if not name or not code:
            QMessageBox.warning(self, "خطا", "نام و کد الزامی هستند.")
            return
        
        categories = {"قهوه": "coffee", "چای": "tea", "شکلات": "chocolate", "دسر": "dessert"}
        category = categories.get(self.category_combo.currentText(), "coffee")
        price = self.price_input.value()
        description = self.description_input.toPlainText().strip() or None
        
        try:
            if self.product_id:
                query = """
                    UPDATE products 
                    SET name = ?, code = ?, category = ?, price = ?, description = ?
                    WHERE id = ?
                """
                self.db.execute_update(query, (name, code, category, price, description, self.product_id))
                QMessageBox.information(self, "موفق", "محصول با موفقیت ویرایش شد.")
            else:
                query = """
                    INSERT INTO products (name, code, category, price, description)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.db.execute_update(query, (name, code, category, price, description))
                QMessageBox.information(self, "موفق", "محصول با موفقیت افزوده شد.")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره محصول: {str(e)}")
