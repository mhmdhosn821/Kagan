"""
صفحه گزارشات
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta


class ReportsPage(QWidget):
    """صفحه گزارشات"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # فیلتر تاریخ
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("از تاریخ:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel("تا تاریخ:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)
        
        # نوع گزارش
        filter_layout.addWidget(QLabel("نوع گزارش:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["فروش", "موجودی انبار", "کمیسیون آرایشگران", "سود خالص واقعی"])
        filter_layout.addWidget(self.report_type_combo)
        
        refresh_btn = QPushButton("🔄 نمایش گزارش")
        refresh_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # خلاصه مالی
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        self.summary_layout = QHBoxLayout()
        self.summary_frame.setLayout(self.summary_layout)
        layout.addWidget(self.summary_frame)
        
        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.report_table)
        
        self.setLayout(layout)
        
        # استایل
        self.setStyleSheet("""
            #summaryFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
        """)
        
        self.load_report()
    
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """ایجاد کارت خلاصه"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def load_report(self):
        """بارگذاری گزارش"""
        # پاک کردن خلاصه قبلی
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        report_type = self.report_type_combo.currentText()
        
        if report_type == "فروش":
            self.load_sales_report(from_date, to_date)
        elif report_type == "موجودی انبار":
            self.load_inventory_report()
        elif report_type == "کمیسیون آرایشگران":
            self.load_commission_report(from_date, to_date)
        elif report_type == "سود خالص واقعی":
            self.load_net_profit_report(from_date, to_date)
    
    def load_sales_report(self, from_date: str, to_date: str):
        """گزارش فروش"""
        # خلاصه
        query = """
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(total_amount), 0) as total,
                COALESCE(SUM(discount_amount), 0) as discount
            FROM invoices
            WHERE DATE(created_at) BETWEEN ? AND ?
        """
        result = self.db.execute_query(query, (from_date, to_date))
        
        if result:
            row = result[0]
            self.summary_layout.addWidget(
                self.create_summary_card("تعداد فاکتورها", str(row['count']), "#3498db")
            )
            self.summary_layout.addWidget(
                self.create_summary_card("مجموع فروش", f"{row['total']:,.0f} ریال", "#27ae60")
            )
            self.summary_layout.addWidget(
                self.create_summary_card("مجموع تخفیف", f"{row['discount']:,.0f} ریال", "#e74c3c")
            )
        
        # جزئیات
        query = """
            SELECT 
                DATE(created_at) as date,
                invoice_type,
                COUNT(*) as count,
                SUM(total_amount) as total
            FROM invoices
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at), invoice_type
            ORDER BY date DESC
        """
        data = self.db.execute_query(query, (from_date, to_date))
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع", "تعداد فاکتور", "مبلغ"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(data))
        
        invoice_types = {"cafe": "کافه", "barbershop": "آرایشگاه", "mixed": "ترکیبی"}
        
        for i, row in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(row['date']))
            self.report_table.setItem(i, 1, QTableWidgetItem(invoice_types.get(row['invoice_type'], row['invoice_type'])))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(row['count'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{row['total']:,.0f} ریال"))
    
    def load_inventory_report(self):
        """گزارش موجودی انبار"""
        # خلاصه
        query = """
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(quantity * unit_price), 0) as total_value
            FROM inventory
        """
        result = self.db.execute_query(query)
        
        if result:
            row = result[0]
            self.summary_layout.addWidget(
                self.create_summary_card("تعداد کالاها", str(row['count']), "#3498db")
            )
            self.summary_layout.addWidget(
                self.create_summary_card("ارزش کل انبار", f"{row['total_value']:,.0f} ریال", "#27ae60")
            )
        
        # جزئیات
        query = """
            SELECT 
                name, code, inventory_type, quantity, unit, unit_price,
                (quantity * unit_price) as total_value
            FROM inventory
            ORDER BY total_value DESC
        """
        data = self.db.execute_query(query)
        
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "نام", "کد", "نوع انبار", "موجودی", "قیمت واحد", "ارزش کل"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(data))
        
        inventory_types = {"cafe": "کافه", "barbershop": "آرایشگاه"}
        units = {"liter": "لیتر", "kg": "کیلوگرم", "gram": "گرم", "ml": "میلی‌لیتر", "unit": "عدد"}
        
        for i, row in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(row['name']))
            self.report_table.setItem(i, 1, QTableWidgetItem(row['code']))
            self.report_table.setItem(i, 2, QTableWidgetItem(inventory_types.get(row['inventory_type'], row['inventory_type'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{row['quantity']:.1f} {units.get(row['unit'], row['unit'])}"))
            self.report_table.setItem(i, 4, QTableWidgetItem(f"{row['unit_price']:,.0f}"))
            self.report_table.setItem(i, 5, QTableWidgetItem(f"{row['total_value']:,.0f} ریال"))
    
    def load_commission_report(self, from_date: str, to_date: str):
        """گزارش کمیسیون"""
        # خلاصه
        query = """
            SELECT 
                COUNT(DISTINCT ii.barber_id) as barber_count,
                COALESCE(SUM(ii.total_price), 0) as total_sales
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE ii.barber_id IS NOT NULL
            AND DATE(i.created_at) BETWEEN ? AND ?
        """
        result = self.db.execute_query(query, (from_date, to_date))
        
        if result:
            row = result[0]
            self.summary_layout.addWidget(
                self.create_summary_card("تعداد آرایشگران", str(row['barber_count']), "#3498db")
            )
            self.summary_layout.addWidget(
                self.create_summary_card("مجموع فروش", f"{row['total_sales']:,.0f} ریال", "#27ae60")
            )
        
        # جزئیات
        query = """
            SELECT 
                u.full_name as barber_name,
                u.commission_percentage,
                COUNT(ii.id) as service_count,
                SUM(ii.total_price) as total_sales,
                SUM(ii.total_price * u.commission_percentage / 100) as commission
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            JOIN users u ON ii.barber_id = u.id
            WHERE ii.barber_id IS NOT NULL
            AND DATE(i.created_at) BETWEEN ? AND ?
            GROUP BY ii.barber_id, u.full_name, u.commission_percentage
            ORDER BY total_sales DESC
        """
        data = self.db.execute_query(query, (from_date, to_date))
        
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "آرایشگر", "درصد کمیسیون", "تعداد خدمات", "فروش", "کمیسیون"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(data))
        
        for i, row in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(row['barber_name']))
            self.report_table.setItem(i, 1, QTableWidgetItem(f"{row['commission_percentage']:.0f}%"))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(row['service_count'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{row['total_sales']:,.0f} ریال"))
            self.report_table.setItem(i, 4, QTableWidgetItem(f"{row['commission']:,.0f} ریال"))
    
    def load_net_profit_report(self, from_date: str, to_date: str):
        """گزارش سود خالص واقعی"""
        # محاسبه فروش کل
        total_sales_query = """
            SELECT COALESCE(SUM(total_amount), 0) as total
            FROM invoices
            WHERE DATE(created_at) BETWEEN ? AND ?
        """
        sales_result = self.db.execute_query(total_sales_query, (from_date, to_date))
        total_sales = sales_result[0]['total'] if sales_result else 0
        
        # محاسبه هزینه مواد مصرفی (تخمینی بر اساس کسر موجودی)
        # این مقدار می‌تواند بر اساس سیستم BOM دقیق‌تر محاسبه شود
        material_cost_query = """
            SELECT COALESCE(SUM(quantity * unit_price), 0) as cost
            FROM inventory
            WHERE inventory_type IN ('cafe', 'barbershop')
            AND item_type IN ('raw_material', 'consumable')
        """
        material_result = self.db.execute_query(material_cost_query, ())
        # فرض: 30% از ارزش انبار در این بازه مصرف شده
        material_cost = (material_result[0]['cost'] * 0.3) if material_result else 0
        
        # محاسبه کمیسیون آرایشگران
        commission_query = """
            SELECT COALESCE(SUM(ii.total_price * u.commission_percentage / 100), 0) as total
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            JOIN users u ON ii.barber_id = u.id
            WHERE ii.barber_id IS NOT NULL
            AND DATE(i.created_at) BETWEEN ? AND ?
        """
        commission_result = self.db.execute_query(commission_query, (from_date, to_date))
        total_commission = commission_result[0]['total'] if commission_result else 0
        
        # محاسبه هزینه‌های جاری
        expenses_query = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE DATE(date) BETWEEN ? AND ?
        """
        expenses_result = self.db.execute_query(expenses_query, (from_date, to_date))
        total_expenses = expenses_result[0]['total'] if expenses_result else 0
        
        # محاسبه سود خالص
        net_profit = total_sales - material_cost - total_commission - total_expenses
        
        # نمایش کارت‌های خلاصه
        self.summary_layout.addWidget(
            self.create_summary_card("فروش کل", f"{total_sales:,.0f} ریال", "#10B981")
        )
        self.summary_layout.addWidget(
            self.create_summary_card("هزینه مواد", f"{material_cost:,.0f} ریال", "#F59E0B")
        )
        self.summary_layout.addWidget(
            self.create_summary_card("کمیسیون", f"{total_commission:,.0f} ریال", "#F59E0B")
        )
        self.summary_layout.addWidget(
            self.create_summary_card("هزینه‌های جاری", f"{total_expenses:,.0f} ریال", "#EF4444")
        )
        self.summary_layout.addWidget(
            self.create_summary_card("سود خالص", f"{net_profit:,.0f} ریال", "#6366F1")
        )
        
        # جدول تفصیلی
        self.report_table.setColumnCount(2)
        self.report_table.setHorizontalHeaderLabels(["مورد", "مبلغ"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(5)
        
        items = [
            ("فروش کل", total_sales, "#10B981"),
            ("منهای: هزینه مواد مصرفی", -material_cost, "#F59E0B"),
            ("منهای: کمیسیون آرایشگران", -total_commission, "#F59E0B"),
            ("منهای: هزینه‌های جاری", -total_expenses, "#EF4444"),
            ("سود خالص", net_profit, "#6366F1"),
        ]
        
        for i, (label, value, color) in enumerate(items):
            item_label = QTableWidgetItem(label)
            if i == 4:  # سود خالص
                font = QFont()
                font.setBold(True)
                item_label.setFont(font)
            self.report_table.setItem(i, 0, item_label)
            
            item_value = QTableWidgetItem(f"{abs(value):,.0f} ریال")
            if i == 4:  # سود خالص
                item_value.setFont(font)
            self.report_table.setItem(i, 1, item_value)
