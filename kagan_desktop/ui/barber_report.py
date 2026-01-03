"""
صفحه گزارش عملکرد آرایشگران
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit
)
from PyQt6.QtCore import Qt, QDate


class BarberReportPage(QWidget):
    """صفحه گزارش عملکرد آرایشگران"""
    
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # فیلترها
        filter_layout = QHBoxLayout()
        
        # تاریخ شروع
        filter_layout.addWidget(QLabel("از تاریخ:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date)
        
        # تاریخ پایان
        filter_layout.addWidget(QLabel("تا تاریخ:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        
        # دکمه نمایش
        show_btn = QPushButton("📊 نمایش گزارش")
        show_btn.setObjectName("primaryButton")
        show_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(show_btn)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "نام آرایشگر", "تعداد خدمات", "درآمد کل (ریال)", "کمیسیون (%)", "کمیسیون دریافتی (ریال)"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.report_table)
        
        self.setLayout(layout)
        self.load_report()
    
    def load_report(self):
        """بارگذاری گزارش عملکرد"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT 
                u.id,
                u.full_name,
                u.commission_percentage,
                COUNT(DISTINCT ii.id) as service_count,
                SUM(ii.total_price) as total_revenue
            FROM users u
            LEFT JOIN invoice_items ii ON u.id = ii.barber_id
            LEFT JOIN invoices inv ON ii.invoice_id = inv.id
            WHERE u.role = 'barber' 
                AND (ii.barber_id IS NULL OR (inv.created_at >= ? AND inv.created_at <= ?))
            GROUP BY u.id, u.full_name, u.commission_percentage
            ORDER BY total_revenue DESC
        """
        
        barbers = self.db.execute_query(query, (start_date, end_date))
        
        self.report_table.setRowCount(len(barbers))
        
        for i, barber in enumerate(barbers):
            self.report_table.setItem(i, 0, QTableWidgetItem(barber['full_name']))
            
            service_count = barber['service_count'] or 0
            self.report_table.setItem(i, 1, QTableWidgetItem(str(service_count)))
            
            total_revenue = barber['total_revenue'] or 0
            self.report_table.setItem(i, 2, QTableWidgetItem(f"{total_revenue:,.0f}"))
            
            commission_pct = barber['commission_percentage']
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{commission_pct}%"))
            
            commission_amount = total_revenue * commission_pct / 100
            self.report_table.setItem(i, 4, QTableWidgetItem(f"{commission_amount:,.0f}"))
