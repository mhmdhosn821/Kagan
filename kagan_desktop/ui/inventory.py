"""
صفحه مدیریت انبار دوگانه
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt


class InventoryPage(QWidget):
    """صفحه مدیریت انبار"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # تب‌ها برای انبار کافه و آرایشگاه
        tabs = QTabWidget()
        
        # تب انبار کافه
        cafe_tab = self.create_inventory_tab("cafe")
        tabs.addTab(cafe_tab, "☕ انبار کافه")
        
        # تب انبار آرایشگاه
        barbershop_tab = self.create_inventory_tab("barbershop")
        tabs.addTab(barbershop_tab, "💇 انبار آرایشگاه")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_inventory_tab(self, inventory_type: str) -> QWidget:
        """ایجاد تب انبار"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        # جستجو
        search_input = QLineEdit()
        search_input.setPlaceholderText("جستجو...")
        search_input.setObjectName(f"search_{inventory_type}")
        toolbar.addWidget(search_input)
        
        # دکمه افزودن
        add_btn = QPushButton("➕ افزودن کالا")
        add_btn.clicked.connect(lambda: self.add_item(inventory_type))
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول
        table = QTableWidget()
        table.setObjectName(f"table_{inventory_type}")
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "نام", "کد", "نوع", "واحد", "موجودی", "حداقل", "قیمت واحد", "عملیات"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(table)
        
        widget.setLayout(layout)
        
        # بارگذاری داده‌ها
        search_input.textChanged.connect(lambda: self.load_inventory(inventory_type, table, search_input))
        self.load_inventory(inventory_type, table, search_input)
        
        return widget
    
    def load_inventory(self, inventory_type: str, table: QTableWidget, search_input: QLineEdit):
        """بارگذاری کالاهای انبار"""
        search = search_input.text().strip()
        
        if search:
            query = """
                SELECT * FROM inventory 
                WHERE inventory_type = ? AND (name LIKE ? OR code LIKE ?)
                ORDER BY name
            """
            items = self.db.execute_query(query, (inventory_type, f"%{search}%", f"%{search}%"))
        else:
            query = "SELECT * FROM inventory WHERE inventory_type = ? ORDER BY name"
            items = self.db.execute_query(query, (inventory_type,))
        
        table.setRowCount(len(items))
        
        item_types = {
            "raw_material": "مواد اولیه",
            "consumable": "مواد مصرفی",
            "product": "محصول"
        }
        
        units = {
            "liter": "لیتر",
            "kg": "کیلوگرم",
            "gram": "گرم",
            "ml": "میلی‌لیتر",
            "unit": "عدد"
        }
        
        for i, item in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(item['name']))
            table.setItem(i, 1, QTableWidgetItem(item['code']))
            table.setItem(i, 2, QTableWidgetItem(item_types.get(item['item_type'], item['item_type'])))
            table.setItem(i, 3, QTableWidgetItem(units.get(item['unit'], item['unit'])))
            
            # موجودی با رنگ
            qty_item = QTableWidgetItem(f"{item['quantity']:.1f}")
            if item['quantity'] <= item['min_stock_alert']:
                qty_item.setForeground(Qt.GlobalColor.red)
            table.setItem(i, 4, qty_item)
            
            table.setItem(i, 5, QTableWidgetItem(f"{item['min_stock_alert']:.1f}"))
            table.setItem(i, 6, QTableWidgetItem(f"{item['unit_price']:,.0f}"))
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            add_stock_btn = QPushButton("➕")
            add_stock_btn.setMaximumWidth(30)
            add_stock_btn.clicked.connect(lambda checked, iid=item['id']: self.add_stock(iid))
            actions_layout.addWidget(add_stock_btn)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, iid=item['id']: self.edit_item(iid))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            table.setCellWidget(i, 7, actions_widget)
    
    def add_item(self, inventory_type: str):
        """افزودن کالای جدید"""
        dialog = InventoryDialog(self.db, None, inventory_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # پیدا کردن تب و جدول مناسب
            table = self.findChild(QTableWidget, f"table_{inventory_type}")
            search = self.findChild(QLineEdit, f"search_{inventory_type}")
            if table and search:
                self.load_inventory(inventory_type, table, search)
    
    def edit_item(self, item_id: int):
        """ویرایش کالا"""
        # دریافت نوع انبار
        query = "SELECT inventory_type FROM inventory WHERE id = ?"
        result = self.db.execute_query(query, (item_id,))
        if result:
            inventory_type = result[0]['inventory_type']
            dialog = InventoryDialog(self.db, item_id, inventory_type, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                table = self.findChild(QTableWidget, f"table_{inventory_type}")
                search = self.findChild(QLineEdit, f"search_{inventory_type}")
                if table and search:
                    self.load_inventory(inventory_type, table, search)
    
    def add_stock(self, item_id: int):
        """افزودن موجودی"""
        dialog = AddStockDialog(self.db, item_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # بروزرسانی جداول
            query = "SELECT inventory_type FROM inventory WHERE id = ?"
            result = self.db.execute_query(query, (item_id,))
            if result:
                inventory_type = result[0]['inventory_type']
                table = self.findChild(QTableWidget, f"table_{inventory_type}")
                search = self.findChild(QLineEdit, f"search_{inventory_type}")
                if table and search:
                    self.load_inventory(inventory_type, table, search)


class InventoryDialog(QDialog):
    """دیالوگ افزودن/ویرایش کالا"""
    
    def __init__(self, db, item_id, inventory_type, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.inventory_type = inventory_type
        self.init_ui()
        
        if item_id:
            self.load_item()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن کالا" if not self.item_id else "ویرایش کالا")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # نام
        self.name_input = QLineEdit()
        layout.addRow("نام:", self.name_input)
        
        # کد
        self.code_input = QLineEdit()
        layout.addRow("کد:", self.code_input)
        
        # نوع کالا
        self.item_type_combo = QComboBox()
        if self.inventory_type == "cafe":
            self.item_type_combo.addItems(["مواد اولیه"])
            self.item_type_combo.setItemData(0, "raw_material")
        else:
            self.item_type_combo.addItems(["مواد مصرفی", "محصول"])
            self.item_type_combo.setItemData(0, "consumable")
            self.item_type_combo.setItemData(1, "product")
        layout.addRow("نوع:", self.item_type_combo)
        
        # واحد
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["لیتر", "کیلوگرم", "گرم", "میلی‌لیتر", "عدد"])
        units_data = ["liter", "kg", "gram", "ml", "unit"]
        for i, unit in enumerate(units_data):
            self.unit_combo.setItemData(i, unit)
        layout.addRow("واحد:", self.unit_combo)
        
        # موجودی اولیه
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(1000000)
        self.quantity_input.setDecimals(2)
        layout.addRow("موجودی اولیه:", self.quantity_input)
        
        # حداقل موجودی
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(1000000)
        self.min_stock_input.setDecimals(2)
        layout.addRow("حداقل موجودی:", self.min_stock_input)
        
        # قیمت واحد
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1000000000)
        self.price_input.setDecimals(0)
        layout.addRow("قیمت واحد:", self.price_input)
        
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
    
    def load_item(self):
        """بارگذاری اطلاعات کالا"""
        query = "SELECT * FROM inventory WHERE id = ?"
        result = self.db.execute_query(query, (self.item_id,))
        
        if result:
            item = result[0]
            self.name_input.setText(item['name'])
            self.code_input.setText(item['code'])
            
            # نوع کالا
            item_type_index = 0
            if item['item_type'] == "product":
                item_type_index = 1
            self.item_type_combo.setCurrentIndex(item_type_index)
            
            # واحد
            units = ["liter", "kg", "gram", "ml", "unit"]
            if item['unit'] in units:
                self.unit_combo.setCurrentIndex(units.index(item['unit']))
            
            self.quantity_input.setValue(item['quantity'])
            self.min_stock_input.setValue(item['min_stock_alert'])
            self.price_input.setValue(item['unit_price'])
    
    def save(self):
        """ذخیره کالا"""
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()
        
        if not name or not code:
            QMessageBox.warning(self, "خطا", "نام و کد الزامی هستند.")
            return
        
        item_types = {"مواد اولیه": "raw_material", "مواد مصرفی": "consumable", "محصول": "product"}
        item_type = item_types.get(self.item_type_combo.currentText(), "raw_material")
        
        units = ["liter", "kg", "gram", "ml", "unit"]
        unit = units[self.unit_combo.currentIndex()]
        
        quantity = self.quantity_input.value()
        min_stock = self.min_stock_input.value()
        price = self.price_input.value()
        
        try:
            if self.item_id:
                query = """
                    UPDATE inventory 
                    SET name = ?, code = ?, item_type = ?, unit = ?, 
                        quantity = ?, min_stock_alert = ?, unit_price = ?
                    WHERE id = ?
                """
                self.db.execute_update(query, (name, code, item_type, unit, quantity, min_stock, price, self.item_id))
                QMessageBox.information(self, "موفق", "کالا با موفقیت ویرایش شد.")
            else:
                query = """
                    INSERT INTO inventory (name, code, inventory_type, item_type, unit, quantity, min_stock_alert, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute_update(query, (name, code, self.inventory_type, item_type, unit, quantity, min_stock, price))
                QMessageBox.information(self, "موفق", "کالا با موفقیت افزوده شد.")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره کالا: {str(e)}")


class AddStockDialog(QDialog):
    """دیالوگ افزودن موجودی"""
    
    def __init__(self, db, item_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن موجودی")
        self.setMinimumWidth(300)
        
        layout = QFormLayout()
        
        # دریافت نام کالا
        query = "SELECT name, quantity, unit FROM inventory WHERE id = ?"
        result = self.db.execute_query(query, (self.item_id,))
        
        if result:
            item = result[0]
            name_label = QLabel(f"کالا: {item['name']}")
            layout.addRow(name_label)
            
            current_label = QLabel(f"موجودی فعلی: {item['quantity']:.2f} {item['unit']}")
            layout.addRow(current_label)
        
        # مقدار افزایش
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(1000000)
        self.quantity_input.setDecimals(2)
        layout.addRow("مقدار افزایش:", self.quantity_input)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("افزودن")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
    
    def save(self):
        """افزودن موجودی"""
        quantity = self.quantity_input.value()
        
        if quantity <= 0:
            QMessageBox.warning(self, "خطا", "مقدار باید بیشتر از صفر باشد.")
            return
        
        try:
            query = "UPDATE inventory SET quantity = quantity + ? WHERE id = ?"
            self.db.execute_update(query, (quantity, self.item_id))
            QMessageBox.information(self, "موفق", "موجودی با موفقیت افزوده شد.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن موجودی: {str(e)}")
