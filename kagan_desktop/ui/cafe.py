"""
صفحه بخش کافه
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt

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
            actions_layout.setSpacing(5)
            
            recipe_btn = QPushButton("📝 دستور")
            recipe_btn.setObjectName("infoButton")
            recipe_btn.setMinimumWidth(80)
            recipe_btn.clicked.connect(lambda checked, pid=product['id']: self.manage_recipe(pid))
            actions_layout.addWidget(recipe_btn)
            
            edit_btn = QPushButton("✏️ ویرایش")
            edit_btn.setObjectName("primaryButton")
            edit_btn.setMinimumWidth(80)
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
    
    def manage_recipe(self, product_id: int):
        """مدیریت دستور ساخت محصول"""
        dialog = RecipeDialog(self.db, product_id, self)
        dialog.exec()


class RecipeDialog(QDialog):
    """دیالوگ مدیریت دستور ساخت (Recipe) چند مادهای"""
    
    def __init__(self, db, product_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.init_ui()
        self.load_recipe()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        # دریافت نام محصول
        query = "SELECT name FROM products WHERE id = ?"
        result = self.db.execute_query(query, (self.product_id,))
        product_name = result[0]['name'] if result else "محصول"
        
        self.setWindowTitle(f"دستور ساخت - {product_name}")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        # توضیحات
        info_label = QLabel("مواد اولیه مورد نیاز برای ساخت این محصول:")
        layout.addWidget(info_label)
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        add_ingredient_btn = QPushButton("➕ افزودن ماده")
        add_ingredient_btn.setObjectName("successButton")
        add_ingredient_btn.clicked.connect(self.add_ingredient)
        toolbar.addWidget(add_ingredient_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # جدول مواد
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(5)
        self.ingredients_table.setHorizontalHeaderLabels([
            "ماده اولیه", "مقدار", "واحد", "موجودی انبار", "عملیات"
        ])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ingredients_table.setAlternatingRowColors(True)
        self.ingredients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.ingredients_table)
        
        # دکمه بستن
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_recipe(self):
        """بارگذاری دستور ساخت"""
        query = """
            SELECT 
                pr.id,
                pr.quantity,
                i.id as inventory_id,
                i.name,
                i.unit,
                i.quantity as stock_quantity
            FROM product_recipe pr
            JOIN inventory i ON pr.inventory_id = i.id
            WHERE pr.product_id = ?
            ORDER BY i.name
        """
        ingredients = self.db.execute_query(query, (self.product_id,))
        
        self.ingredients_table.setRowCount(len(ingredients))
        
        units = {
            "liter": "لیتر",
            "kg": "کیلوگرم",
            "gram": "گرم",
            "ml": "میلی‌لیتر",
            "unit": "عدد"
        }
        
        for i, ing in enumerate(ingredients):
            self.ingredients_table.setItem(i, 0, QTableWidgetItem(ing['name']))
            self.ingredients_table.setItem(i, 1, QTableWidgetItem(f"{ing['quantity']:.2f}"))
            self.ingredients_table.setItem(i, 2, QTableWidgetItem(units.get(ing['unit'], ing['unit'])))
            
            # موجودی با رنگ
            stock_item = QTableWidgetItem(f"{ing['stock_quantity']:.2f}")
            if ing['stock_quantity'] < ing['quantity']:
                stock_item.setForeground(Qt.GlobalColor.red)
            self.ingredients_table.setItem(i, 3, stock_item)
            
            # دکمه حذف
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(lambda checked, rid=ing['id']: self.delete_ingredient(rid))
            self.ingredients_table.setCellWidget(i, 4, delete_btn)
    
    def add_ingredient(self):
        """افزودن ماده به دستور"""
        dialog = AddIngredientDialog(self.db, self.product_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_recipe()
    
    def delete_ingredient(self, recipe_id: int):
        """حذف ماده از دستور"""
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا از حذف این ماده اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM product_recipe WHERE id = ?"
            self.db.execute_update(query, (recipe_id,))
            QMessageBox.information(self, "موفق", "ماده از دستور حذف شد.")
            self.load_recipe()


class AddIngredientDialog(QDialog):
    """دیالوگ افزودن ماده به دستور"""
    
    def __init__(self, db, product_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن ماده")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # انتخاب ماده اولیه
        self.inventory_combo = QComboBox()
        self.load_inventory_items()
        layout.addRow("ماده اولیه:", self.inventory_combo)
        
        # مقدار
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(100000)
        self.quantity_input.setDecimals(2)
        layout.addRow("مقدار:", self.quantity_input)
        
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
    
    def load_inventory_items(self):
        """بارگذاری لیست مواد اولیه انبار کافه"""
        query = """
            SELECT id, name, unit, quantity 
            FROM inventory 
            WHERE inventory_type = 'cafe' AND item_type = 'raw_material'
            ORDER BY name
        """
        items = self.db.execute_query(query)
        
        for item in items:
            display_text = f"{item['name']} (موجودی: {item['quantity']:.2f} {item['unit']})"
            self.inventory_combo.addItem(display_text, item['id'])
        
        if not items:
            QMessageBox.warning(self, "توجه", "هیچ ماده اولیهای در انبار کافه وجود ندارد.")
    
    def save(self):
        """ذخیره ماده در دستور"""
        if self.inventory_combo.count() == 0:
            return
        
        inventory_id = self.inventory_combo.currentData()
        quantity = self.quantity_input.value()
        
        if quantity <= 0:
            QMessageBox.warning(self, "خطا", "مقدار باید بیشتر از صفر باشد.")
            return
        
        # بررسی تکراری نبودن
        query = "SELECT id FROM product_recipe WHERE product_id = ? AND inventory_id = ?"
        existing = self.db.execute_query(query, (self.product_id, inventory_id))
        
        if existing:
            QMessageBox.warning(self, "خطا", "این ماده قبلاً به دستور افزوده شده است.")
            return
        
        try:
            query = """
                INSERT INTO product_recipe (product_id, inventory_id, quantity)
                VALUES (?, ?, ?)
            """
            self.db.execute_update(query, (self.product_id, inventory_id, quantity))
            QMessageBox.information(self, "موفق", "ماده به دستور افزوده شد.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن ماده: {str(e)}")


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
