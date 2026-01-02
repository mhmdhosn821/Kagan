"""
صفحه داشبورد
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta


class DashboardPage(QWidget):
    """صفحه داشبورد"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # کارت‌های آماری
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # فروش امروز
        today_sales = self.get_today_sales()
        stats_layout.addWidget(self.create_stat_card(
            "💰", "فروش امروز", f"{today_sales:,} ریال", "#27ae60"
        ), 0, 0)
        
        # فروش این ماه
        month_sales = self.get_month_sales()
        stats_layout.addWidget(self.create_stat_card(
            "📊", "فروش این ماه", f"{month_sales:,} ریال", "#3498db"
        ), 0, 1)
        
        # تعداد مشتریان
        customers_count = self.get_customers_count()
        stats_layout.addWidget(self.create_stat_card(
            "👥", "تعداد مشتریان", str(customers_count), "#9b59b6"
        ), 0, 2)
        
        # هشدار موجودی
        low_stock_count = self.get_low_stock_count()
        stats_layout.addWidget(self.create_stat_card(
            "⚠️", "هشدار موجودی", str(low_stock_count), "#e74c3c"
        ), 0, 3)
        
        layout.addLayout(stats_layout)
        
        # بخش آخرین فاکتورها
        invoices_section = QVBoxLayout()
        
        invoices_title = QLabel("آخرین فاکتورها")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        invoices_title.setFont(title_font)
        invoices_section.addWidget(invoices_title)
        
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            "شماره فاکتور", "نوع", "مشتری", "مبلغ", "تاریخ", "وضعیت"
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.load_recent_invoices()
        
        invoices_section.addWidget(self.invoices_table)
        layout.addLayout(invoices_section)
        
        # بخش هشدارهای موجودی
        if low_stock_count > 0:
            alerts_section = QVBoxLayout()
            
            alerts_title = QLabel("⚠️ هشدارهای موجودی")
            alerts_title.setFont(title_font)
            alerts_title.setStyleSheet("color: #e74c3c;")
            alerts_section.addWidget(alerts_title)
            
            self.alerts_table = QTableWidget()
            self.alerts_table.setColumnCount(4)
            self.alerts_table.setHorizontalHeaderLabels([
                "نام کالا", "کد", "موجودی فعلی", "حداقل موجودی"
            ])
            self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.alerts_table.setAlternatingRowColors(True)
            self.alerts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.alerts_table.setMaximumHeight(200)
            self.load_stock_alerts()
            
            alerts_section.addWidget(self.alerts_table)
            layout.addLayout(alerts_section)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # استایل
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
    
    def create_stat_card(self, icon: str, title: str, value: str, color: str) -> QFrame:
        """ایجاد کارت آماری"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            #statCard {{
                background-color: white;
                border-radius: 10px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # ردیف اول: آیکون و عنوان
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px;")
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        top_layout.addWidget(title_label)
        
        layout.addLayout(top_layout)
        
        # مقدار
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def get_today_sales(self) -> float:
        """فروش امروز"""
        today = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM invoices 
            WHERE DATE(created_at) = ?
        """
        result = self.db.execute_query(query, (today,))
        return result[0][0] if result else 0
    
    def get_month_sales(self) -> float:
        """فروش این ماه"""
        month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        query = """
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM invoices 
            WHERE DATE(created_at) >= ?
        """
        result = self.db.execute_query(query, (month_start,))
        return result[0][0] if result else 0
    
    def get_customers_count(self) -> int:
        """تعداد مشتریان"""
        query = "SELECT COUNT(*) FROM customers"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0
    
    def get_low_stock_count(self) -> int:
        """تعداد کالاهای با موجودی کم"""
        query = "SELECT COUNT(*) FROM inventory WHERE quantity <= min_stock_alert"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0
    
    def load_recent_invoices(self):
        """بارگذاری آخرین فاکتورها"""
        query = """
            SELECT i.invoice_number, i.invoice_type, c.name as customer_name, 
                   i.total_amount, i.created_at, i.status
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT 10
        """
        invoices = self.db.execute_query(query)
        
        self.invoices_table.setRowCount(len(invoices))
        
        invoice_types = {
            "cafe": "کافه",
            "barbershop": "آرایشگاه",
            "mixed": "ترکیبی"
        }
        
        for i, invoice in enumerate(invoices):
            self.invoices_table.setItem(i, 0, QTableWidgetItem(invoice['invoice_number']))
            self.invoices_table.setItem(i, 1, QTableWidgetItem(invoice_types.get(invoice['invoice_type'], invoice['invoice_type'])))
            self.invoices_table.setItem(i, 2, QTableWidgetItem(invoice['customer_name'] or "مشتری عمومی"))
            self.invoices_table.setItem(i, 3, QTableWidgetItem(f"{invoice['total_amount']:,.0f} ریال"))
            
            # فرمت تاریخ
            created_at = invoice['created_at']
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at)
                    date_str = dt.strftime("%Y/%m/%d %H:%M")
                except:
                    date_str = created_at
            else:
                date_str = "-"
            self.invoices_table.setItem(i, 4, QTableWidgetItem(date_str))
            
            status_item = QTableWidgetItem("پرداخت شده" if invoice['status'] == 'paid' else invoice['status'])
            status_item.setForeground(Qt.GlobalColor.darkGreen if invoice['status'] == 'paid' else Qt.GlobalColor.darkRed)
            self.invoices_table.setItem(i, 5, status_item)
    
    def load_stock_alerts(self):
        """بارگذاری هشدارهای موجودی"""
        query = """
            SELECT name, code, quantity, min_stock_alert
            FROM inventory
            WHERE quantity <= min_stock_alert
            ORDER BY quantity ASC
            LIMIT 10
        """
        items = self.db.execute_query(query)
        
        self.alerts_table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            self.alerts_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.alerts_table.setItem(i, 1, QTableWidgetItem(item['code']))
            
            qty_item = QTableWidgetItem(f"{item['quantity']:.1f}")
            qty_item.setForeground(Qt.GlobalColor.darkRed)
            self.alerts_table.setItem(i, 2, qty_item)
            
            self.alerts_table.setItem(i, 3, QTableWidgetItem(f"{item['min_stock_alert']:.1f}"))
