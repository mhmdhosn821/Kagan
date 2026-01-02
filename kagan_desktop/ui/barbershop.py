"""
صفحه بخش آرایشگاه
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QLabel,
    QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox, QSpinBox, QTextEdit
)


class BarbershopPage(QWidget):
    """صفحه بخش آرایشگاه"""
    
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
        self.search_input.setPlaceholderText("جستجو خدمات...")
        self.search_input.textChanged.connect(self.load_services)
        toolbar.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ افزودن خدمت")
        add_btn.clicked.connect(self.add_service)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # جدول خدمات
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(6)
        self.services_table.setHorizontalHeaderLabels([
            "نام", "دسته", "قیمت", "مدت زمان (دقیقه)", "توضیحات", "عملیات"
        ])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.services_table)
        self.setLayout(layout)
        self.load_services()
    
    def load_services(self):
        """بارگذاری لیست خدمات"""
        search = self.search_input.text().strip()
        
        if search:
            query = "SELECT * FROM services WHERE name LIKE ? ORDER BY name"
            services = self.db.execute_query(query, (f"%{search}%",))
        else:
            query = "SELECT * FROM services ORDER BY name"
            services = self.db.execute_query(query)
        
        self.services_table.setRowCount(len(services))
        
        categories = {
            "haircut": "اصلاح مو",
            "facial": "گریم صورت",
            "coloring": "رنگ",
            "massage": "ماساژ"
        }
        
        for i, service in enumerate(services):
            self.services_table.setItem(i, 0, QTableWidgetItem(service['name']))
            self.services_table.setItem(i, 1, QTableWidgetItem(categories.get(service['category'], service['category'])))
            self.services_table.setItem(i, 2, QTableWidgetItem(f"{service['price']:,.0f} ریال"))
            self.services_table.setItem(i, 3, QTableWidgetItem(str(service['duration_minutes'])))
            self.services_table.setItem(i, 4, QTableWidgetItem(service['description'] or "-"))
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, sid=service['id']: self.edit_service(sid))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            self.services_table.setCellWidget(i, 5, actions_widget)
    
    def add_service(self):
        """افزودن خدمت جدید"""
        dialog = ServiceDialog(self.db, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_services()
    
    def edit_service(self, service_id: int):
        """ویرایش خدمت"""
        dialog = ServiceDialog(self.db, service_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_services()


class ServiceDialog(QDialog):
    """دیالوگ افزودن/ویرایش خدمت"""
    
    def __init__(self, db, service_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.service_id = service_id
        self.init_ui()
        
        if service_id:
            self.load_service()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("افزودن خدمت" if not self.service_id else "ویرایش خدمت")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow("نام:", self.name_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["اصلاح مو", "گریم صورت", "رنگ", "ماساژ"])
        layout.addRow("دسته:", self.category_combo)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(10000000)
        self.price_input.setDecimals(0)
        layout.addRow("قیمت:", self.price_input)
        
        self.duration_input = QSpinBox()
        self.duration_input.setMaximum(300)
        self.duration_input.setValue(30)
        layout.addRow("مدت زمان (دقیقه):", self.duration_input)
        
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
    
    def load_service(self):
        """بارگذاری اطلاعات خدمت"""
        query = "SELECT * FROM services WHERE id = ?"
        result = self.db.execute_query(query, (self.service_id,))
        
        if result:
            service = result[0]
            self.name_input.setText(service['name'])
            
            categories = ["haircut", "facial", "coloring", "massage"]
            if service['category'] in categories:
                self.category_combo.setCurrentIndex(categories.index(service['category']))
            
            self.price_input.setValue(service['price'])
            self.duration_input.setValue(service['duration_minutes'])
            self.description_input.setPlainText(service['description'] or "")
    
    def save(self):
        """ذخیره خدمت"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "خطا", "نام خدمت الزامی است.")
            return
        
        categories = {"اصلاح مو": "haircut", "گریم صورت": "facial", "رنگ": "coloring", "ماساژ": "massage"}
        category = categories.get(self.category_combo.currentText(), "haircut")
        price = self.price_input.value()
        duration = self.duration_input.value()
        description = self.description_input.toPlainText().strip() or None
        
        try:
            if self.service_id:
                query = """
                    UPDATE services 
                    SET name = ?, category = ?, price = ?, duration_minutes = ?, description = ?
                    WHERE id = ?
                """
                self.db.execute_update(query, (name, category, price, duration, description, self.service_id))
                QMessageBox.information(self, "موفق", "خدمت با موفقیت ویرایش شد.")
            else:
                query = """
                    INSERT INTO services (name, category, price, duration_minutes, description)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.db.execute_update(query, (name, category, price, duration, description))
                QMessageBox.information(self, "موفق", "خدمت با موفقیت افزوده شد.")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره خدمت: {str(e)}")
