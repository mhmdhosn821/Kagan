"""
صفحه نوبت‌دهی
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QLabel,
    QFormLayout, QComboBox, QDateTimeEdit, QMessageBox, QTextEdit
)
from PyQt6.QtCore import QDateTime
from datetime import datetime


class BookingPage(QWidget):
    """صفحه نوبت‌دهی"""
    
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
        
        add_btn = QPushButton("➕ رزرو جدید")
        add_btn.clicked.connect(self.add_booking)
        toolbar.addWidget(add_btn)
        
        toolbar.addStretch()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.load_bookings)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # جدول نوبت‌ها
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(7)
        self.bookings_table.setHorizontalHeaderLabels([
            "مشتری", "آرایشگر", "خدمت", "تاریخ و ساعت", "وضعیت", "یادداشت", "عملیات"
        ])
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bookings_table.setAlternatingRowColors(True)
        self.bookings_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.bookings_table)
        self.setLayout(layout)
        self.load_bookings()
    
    def load_bookings(self):
        """بارگذاری لیست نوبت‌ها"""
        query = """
            SELECT b.id, c.name as customer_name, u.full_name as barber_name,
                   s.name as service_name, b.booking_datetime, b.status, b.notes
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN users u ON b.barber_id = u.id
            JOIN services s ON b.service_id = s.id
            ORDER BY b.booking_datetime DESC
        """
        bookings = self.db.execute_query(query)
        
        self.bookings_table.setRowCount(len(bookings))
        
        statuses = {
            "reserved": "رزرو شده",
            "completed": "تکمیل شده",
            "cancelled": "لغو شده"
        }
        
        for i, booking in enumerate(bookings):
            self.bookings_table.setItem(i, 0, QTableWidgetItem(booking['customer_name']))
            self.bookings_table.setItem(i, 1, QTableWidgetItem(booking['barber_name']))
            self.bookings_table.setItem(i, 2, QTableWidgetItem(booking['service_name']))
            
            # فرمت تاریخ
            try:
                dt = datetime.fromisoformat(booking['booking_datetime'])
                date_str = dt.strftime("%Y/%m/%d %H:%M")
            except:
                date_str = booking['booking_datetime']
            self.bookings_table.setItem(i, 3, QTableWidgetItem(date_str))
            
            self.bookings_table.setItem(i, 4, QTableWidgetItem(statuses.get(booking['status'], booking['status'])))
            self.bookings_table.setItem(i, 5, QTableWidgetItem(booking['notes'] or "-"))
            
            # دکمه‌های عملیات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            if booking['status'] == 'reserved':
                complete_btn = QPushButton("✅")
                complete_btn.setMaximumWidth(30)
                complete_btn.clicked.connect(lambda checked, bid=booking['id']: self.complete_booking(bid))
                actions_layout.addWidget(complete_btn)
                
                cancel_btn = QPushButton("❌")
                cancel_btn.setMaximumWidth(30)
                cancel_btn.clicked.connect(lambda checked, bid=booking['id']: self.cancel_booking(bid))
                actions_layout.addWidget(cancel_btn)
            
            actions_widget.setLayout(actions_layout)
            self.bookings_table.setCellWidget(i, 6, actions_widget)
    
    def add_booking(self):
        """افزودن نوبت جدید"""
        dialog = BookingDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_bookings()
    
    def complete_booking(self, booking_id: int):
        """تکمیل نوبت"""
        try:
            query = "UPDATE bookings SET status = 'completed' WHERE id = ?"
            self.db.execute_update(query, (booking_id,))
            QMessageBox.information(self, "موفق", "نوبت تکمیل شد.")
            self.load_bookings()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تکمیل نوبت: {str(e)}")
    
    def cancel_booking(self, booking_id: int):
        """لغو نوبت"""
        reply = QMessageBox.question(
            self,
            "لغو نوبت",
            "آیا مطمئن هستید که می‌خواهید این نوبت را لغو کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "UPDATE bookings SET status = 'cancelled' WHERE id = ?"
                self.db.execute_update(query, (booking_id,))
                QMessageBox.information(self, "موفق", "نوبت لغو شد.")
                self.load_bookings()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در لغو نوبت: {str(e)}")


class BookingDialog(QDialog):
    """دیالوگ رزرو نوبت"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("رزرو نوبت جدید")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # مشتری
        self.customer_combo = QComboBox()
        self.load_customers()
        layout.addRow("مشتری:", self.customer_combo)
        
        # آرایشگر
        self.barber_combo = QComboBox()
        self.load_barbers()
        layout.addRow("آرایشگر:", self.barber_combo)
        
        # خدمت
        self.service_combo = QComboBox()
        self.load_services()
        layout.addRow("خدمت:", self.service_combo)
        
        # تاریخ و ساعت
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDateTime(QDateTime.currentDateTime())
        layout.addRow("تاریخ و ساعت:", self.datetime_input)
        
        # یادداشت
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addRow("یادداشت:", self.notes_input)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("رزرو")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        self.setLayout(layout)
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        query = "SELECT id, name FROM customers ORDER BY name"
        customers = self.db.execute_query(query)
        
        for customer in customers:
            self.customer_combo.addItem(customer['name'], customer['id'])
    
    def load_barbers(self):
        """بارگذاری لیست آرایشگران"""
        query = "SELECT id, full_name FROM users WHERE role = 'barber' AND is_active = 1"
        barbers = self.db.execute_query(query)
        
        for barber in barbers:
            self.barber_combo.addItem(barber['full_name'], barber['id'])
    
    def load_services(self):
        """بارگذاری لیست خدمات"""
        query = "SELECT id, name, price FROM services ORDER BY name"
        services = self.db.execute_query(query)
        
        for service in services:
            self.service_combo.addItem(f"{service['name']} - {service['price']:,.0f} ریال", service['id'])
    
    def save(self):
        """ذخیره نوبت"""
        if self.customer_combo.count() == 0 or self.barber_combo.count() == 0 or self.service_combo.count() == 0:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا مشتری، آرایشگر و خدمت را ثبت کنید.")
            return
        
        customer_id = self.customer_combo.currentData()
        barber_id = self.barber_combo.currentData()
        service_id = self.service_combo.currentData()
        booking_datetime = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        notes = self.notes_input.toPlainText().strip() or None
        
        try:
            query = """
                INSERT INTO bookings (customer_id, barber_id, service_id, booking_datetime, notes)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute_update(query, (customer_id, barber_id, service_id, booking_datetime, notes))
            QMessageBox.information(self, "موفق", "نوبت با موفقیت رزرو شد.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در رزرو نوبت: {str(e)}")
