"""
مدیریت صندوق و تنخواه‌گردان
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QDateEdit, QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox,
    QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database import Database
from utils.jalali import format_jalali_date, gregorian_to_jalali
from datetime import datetime


class CashboxPage(QWidget):
    """صفحه مدیریت صندوق"""
    
    def __init__(self, db: Database, user: dict):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("💰 مدیریت صندوق و تنخواه")
        title.setProperty("heading", "h2")
        layout.addWidget(title)
        
        # کارت‌های خلاصه
        summary_layout = QHBoxLayout()
        
        # موجودی صندوق
        self.balance_card = self.create_summary_card("موجودی صندوق", "0 ریال", "#10B981")
        summary_layout.addWidget(self.balance_card)
        
        # واریزی امروز
        self.today_deposit_card = self.create_summary_card("واریزی امروز", "0 ریال", "#6366F1")
        summary_layout.addWidget(self.today_deposit_card)
        
        # برداشت امروز
        self.today_withdraw_card = self.create_summary_card("برداشت امروز", "0 ریال", "#EF4444")
        summary_layout.addWidget(self.today_withdraw_card)
        
        layout.addLayout(summary_layout)
        
        # دکمه‌های عمل
        action_layout = QHBoxLayout()
        
        deposit_btn = QPushButton("💵 واریز به صندوق")
        deposit_btn.setProperty("success", True)
        deposit_btn.clicked.connect(lambda: self.open_transaction_dialog("deposit"))
        action_layout.addWidget(deposit_btn)
        
        withdraw_btn = QPushButton("💸 برداشت از صندوق")
        withdraw_btn.setProperty("danger", True)
        withdraw_btn.clicked.connect(lambda: self.open_transaction_dialog("withdraw"))
        action_layout.addWidget(withdraw_btn)
        
        bank_transfer_btn = QPushButton("🏦 واریز به بانک")
        bank_transfer_btn.setProperty("warning", True)
        bank_transfer_btn.clicked.connect(lambda: self.open_transaction_dialog("bank_transfer"))
        action_layout.addWidget(bank_transfer_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # فیلتر
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("نوع:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["همه", "واریز", "برداشت", "واریز به بانک"])
        self.type_filter.currentTextChanged.connect(self.load_transactions)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("از:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.dateChanged.connect(self.load_transactions)
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel("تا:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self.load_transactions)
        filter_layout.addWidget(self.to_date)
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.load_transactions)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # جدول تراکنش‌ها
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع", "مبلغ", "توضیحات", "کاربر"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.transactions_table)
        
        self.setLayout(layout)
        
        # بارگذاری داده‌ها
        self.load_transactions()
        self.update_summary()
    
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """ایجاد کارت خلاصه"""
        card = QFrame()
        card.setProperty("statCard", True)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setProperty("subtitle", True)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setProperty("heading", "h2")
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def update_summary(self):
        """بروزرسانی کارت‌های خلاصه"""
        try:
            # موجودی کل
            balance_query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'deposit' THEN amount ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN type IN ('withdraw', 'bank_transfer') THEN amount ELSE 0 END), 0) as balance
                FROM cashbox
            """
            balance_result = self.db.execute_query(balance_query, ())
            balance = balance_result[0]['balance'] if balance_result else 0
            
            # واریزی امروز
            today = datetime.now().date().isoformat()
            today_deposit_query = """
                SELECT COALESCE(SUM(amount), 0) as total
                FROM cashbox
                WHERE type = 'deposit' AND DATE(date) = ?
            """
            deposit_result = self.db.execute_query(today_deposit_query, (today,))
            today_deposit = deposit_result[0]['total'] if deposit_result else 0
            
            # برداشت امروز
            today_withdraw_query = """
                SELECT COALESCE(SUM(amount), 0) as total
                FROM cashbox
                WHERE type IN ('withdraw', 'bank_transfer') AND DATE(date) = ?
            """
            withdraw_result = self.db.execute_query(today_withdraw_query, (today,))
            today_withdraw = withdraw_result[0]['total'] if withdraw_result else 0
            
            # بروزرسانی کارت‌ها
            balance_layout = self.balance_card.layout()
            balance_layout.itemAt(1).widget().setText(f"{balance:,.0f} ریال")
            
            deposit_layout = self.today_deposit_card.layout()
            deposit_layout.itemAt(1).widget().setText(f"{today_deposit:,.0f} ریال")
            
            withdraw_layout = self.today_withdraw_card.layout()
            withdraw_layout.itemAt(1).widget().setText(f"{today_withdraw:,.0f} ریال")
            
        except Exception as e:
            print(f"خطا در بروزرسانی خلاصه: {e}")
    
    def load_transactions(self):
        """بارگذاری تراکنش‌ها"""
        try:
            self.transactions_table.setRowCount(0)
            
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            transaction_type = self.type_filter.currentText()
            
            # ساخت کوئری
            query = """
                SELECT c.*, u.full_name as user_name
                FROM cashbox c
                LEFT JOIN users u ON c.created_by = u.id
                WHERE DATE(c.date) BETWEEN ? AND ?
            """
            params = [from_date, to_date]
            
            if transaction_type != "همه":
                type_map = {
                    "واریز": "deposit",
                    "برداشت": "withdraw",
                    "واریز به بانک": "bank_transfer"
                }
                query += " AND c.type = ?"
                params.append(type_map.get(transaction_type, ""))
            
            query += " ORDER BY c.date DESC, c.created_at DESC"
            
            transactions = self.db.execute_query(query, tuple(params))
            
            for transaction in transactions:
                row_position = self.transactions_table.rowCount()
                self.transactions_table.insertRow(row_position)
                
                # تاریخ
                trans_date = datetime.fromisoformat(transaction['date'])
                self.transactions_table.setItem(row_position, 0,
                    QTableWidgetItem(gregorian_to_jalali(trans_date)))
                
                # نوع
                type_display = self.get_type_display(transaction['type'])
                type_item = QTableWidgetItem(type_display)
                if transaction['type'] == 'deposit':
                    type_item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    type_item.setForeground(Qt.GlobalColor.darkRed)
                self.transactions_table.setItem(row_position, 1, type_item)
                
                # مبلغ
                amount = transaction['amount']
                amount_item = QTableWidgetItem(f"{amount:,.0f} ریال")
                if transaction['type'] == 'deposit':
                    amount_item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    amount_item.setForeground(Qt.GlobalColor.darkRed)
                self.transactions_table.setItem(row_position, 2, amount_item)
                
                # توضیحات
                description = transaction['description'] or "-"
                self.transactions_table.setItem(row_position, 3,
                    QTableWidgetItem(description))
                
                # کاربر
                self.transactions_table.setItem(row_position, 4,
                    QTableWidgetItem(transaction['user_name'] or "-"))
            
            # بروزرسانی خلاصه
            self.update_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری تراکنش‌ها: {str(e)}")
    
    def get_type_display(self, trans_type: str) -> str:
        """نمایش نوع تراکنش به فارسی"""
        type_map = {
            "deposit": "💵 واریز",
            "withdraw": "💸 برداشت",
            "bank_transfer": "🏦 واریز به بانک"
        }
        return type_map.get(trans_type, trans_type)
    
    def open_transaction_dialog(self, trans_type: str):
        """باز کردن دیالوگ تراکنش"""
        dialog = CashboxTransactionDialog(self.db, self.user, trans_type, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_transactions()


class CashboxTransactionDialog(QDialog):
    """دیالوگ تراکنش صندوق"""
    
    def __init__(self, db: Database, user: dict, trans_type: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.trans_type = trans_type
        
        titles = {
            "deposit": "واریز به صندوق",
            "withdraw": "برداشت از صندوق",
            "bank_transfer": "واریز به بانک"
        }
        self.setWindowTitle(titles.get(trans_type, "تراکنش"))
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # فرم
        form = QFormLayout()
        
        # مبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999)
        self.amount_input.setGroupSeparatorShown(True)
        self.amount_input.setSuffix(" ریال")
        form.addRow("مبلغ:", self.amount_input)
        
        # تاریخ
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("تاریخ:", self.date_input)
        
        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("توضیحات...")
        form.addRow("توضیحات:", self.description_input)
        
        layout.addLayout(form)
        
        # دکمه‌ها
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_transaction)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_transaction(self):
        """ذخیره تراکنش"""
        amount = self.amount_input.value()
        description = self.description_input.toPlainText().strip()
        
        if amount <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً مبلغ را وارد کنید")
            return
        
        date = self.date_input.date().toString("yyyy-MM-dd")
        
        try:
            self.db.execute_update(
                """INSERT INTO cashbox (type, amount, description, date, created_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (self.trans_type, amount, description, date, self.user['id'])
            )
            
            QMessageBox.information(self, "موفق", "تراکنش با موفقیت ثبت شد")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره: {str(e)}")
