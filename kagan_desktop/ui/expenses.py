"""
مدیریت هزینه‌های جاری
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QDateEdit, QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from database import Database
from utils.jalali import format_jalali_date, gregorian_to_jalali
from datetime import datetime


class ExpensesPage(QWidget):
    """صفحه مدیریت هزینه‌های جاری"""
    
    def __init__(self, db: Database, user: dict):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("💵 مدیریت هزینه‌های جاری")
        title.setProperty("heading", "h2")
        layout.addWidget(title)
        
        # فیلتر و دکمه‌های عمل
        top_layout = QHBoxLayout()
        
        # فیلتر دسته‌بندی
        top_layout.addWidget(QLabel("دسته:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "همه", "اجاره", "قبوض", "حقوق", "خرید", "تعمیرات", "بازاریابی", "سایر"
        ])
        self.category_filter.currentTextChanged.connect(self.load_expenses)
        top_layout.addWidget(self.category_filter)
        
        # فیلتر تاریخ
        top_layout.addWidget(QLabel("از:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.dateChanged.connect(self.load_expenses)
        top_layout.addWidget(self.from_date)
        
        top_layout.addWidget(QLabel("تا:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self.load_expenses)
        top_layout.addWidget(self.to_date)
        
        top_layout.addStretch()
        
        # دکمه افزودن
        add_btn = QPushButton("➕ افزودن هزینه")
        add_btn.setProperty("success", True)
        add_btn.clicked.connect(self.add_expense)
        top_layout.addWidget(add_btn)
        
        layout.addLayout(top_layout)
        
        # خلاصه هزینه‌ها
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("مجموع: 0 ریال")
        self.total_label.setProperty("heading", "h3")
        summary_layout.addWidget(self.total_label)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # جدول هزینه‌ها
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.setHorizontalHeaderLabels([
            "تاریخ", "عنوان", "دسته", "مبلغ", "توضیحات", "عملیات"
        ])
        self.expenses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.expenses_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.expenses_table)
        
        self.setLayout(layout)
        
        # بارگذاری هزینه‌ها
        self.load_expenses()
    
    def load_expenses(self):
        """بارگذاری لیست هزینه‌ها"""
        try:
            self.expenses_table.setRowCount(0)
            
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            category = self.category_filter.currentText()
            
            # ساخت کوئری
            query = """
                SELECT e.*, u.full_name as creator_name
                FROM expenses e
                LEFT JOIN users u ON e.created_by = u.id
                WHERE DATE(e.date) BETWEEN ? AND ?
            """
            params = [from_date, to_date]
            
            if category != "همه":
                category_map = {
                    "اجاره": "rent",
                    "قبوض": "bills",
                    "حقوق": "salary",
                    "خرید": "purchase",
                    "تعمیرات": "repairs",
                    "بازاریابی": "marketing",
                    "سایر": "other"
                }
                query += " AND e.category = ?"
                params.append(category_map.get(category, "other"))
            
            query += " ORDER BY e.date DESC"
            
            expenses = self.db.execute_query(query, tuple(params))
            
            total_amount = 0
            
            for expense in expenses:
                row_position = self.expenses_table.rowCount()
                self.expenses_table.insertRow(row_position)
                
                # تاریخ
                expense_date = datetime.fromisoformat(expense['date'])
                self.expenses_table.setItem(row_position, 0,
                    QTableWidgetItem(gregorian_to_jalali(expense_date)))
                
                # عنوان
                self.expenses_table.setItem(row_position, 1,
                    QTableWidgetItem(expense['title']))
                
                # دسته
                category_display = self.get_category_display(expense['category'])
                self.expenses_table.setItem(row_position, 2,
                    QTableWidgetItem(category_display))
                
                # مبلغ
                amount = expense['amount']
                total_amount += amount
                self.expenses_table.setItem(row_position, 3,
                    QTableWidgetItem(f"{amount:,.0f} ریال"))
                
                # توضیحات
                description = expense['description'] or "-"
                self.expenses_table.setItem(row_position, 4,
                    QTableWidgetItem(description[:50] + "..." if len(description) > 50 else description))
                
                # دکمه حذف
                delete_btn = QPushButton("🗑️ حذف")
                delete_btn.setProperty("danger", True)
                delete_btn.clicked.connect(lambda checked, eid=expense['id']: self.delete_expense(eid))
                self.expenses_table.setCellWidget(row_position, 5, delete_btn)
            
            # بروزرسانی مجموع
            self.total_label.setText(f"مجموع: {total_amount:,.0f} ریال")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری هزینه‌ها: {str(e)}")
    
    def get_category_display(self, category: str) -> str:
        """نمایش دسته به فارسی"""
        category_map = {
            "rent": "اجاره",
            "bills": "قبوض",
            "salary": "حقوق",
            "purchase": "خرید",
            "repairs": "تعمیرات",
            "marketing": "بازاریابی",
            "other": "سایر"
        }
        return category_map.get(category, category)
    
    def add_expense(self):
        """افزودن هزینه جدید"""
        dialog = ExpenseDialog(self.db, self.user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_expenses()
    
    def delete_expense(self, expense_id: int):
        """حذف هزینه"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا از حذف این هزینه مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute_update(
                    "DELETE FROM expenses WHERE id = ?",
                    (expense_id,)
                )
                QMessageBox.information(self, "موفق", "هزینه با موفقیت حذف شد")
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")


class ExpenseDialog(QDialog):
    """دیالوگ افزودن/ویرایش هزینه"""
    
    def __init__(self, db: Database, user: dict, expense_id: int = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.expense_id = expense_id
        self.setWindowTitle("افزودن هزینه جدید")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # فرم
        form = QFormLayout()
        
        # عنوان
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("مثال: اجاره مغازه")
        form.addRow("عنوان:", self.title_input)
        
        # مبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999)
        self.amount_input.setGroupSeparatorShown(True)
        self.amount_input.setSuffix(" ریال")
        form.addRow("مبلغ:", self.amount_input)
        
        # دسته‌بندی
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "اجاره", "قبوض", "حقوق", "خرید", "تعمیرات", "بازاریابی", "سایر"
        ])
        form.addRow("دسته:", self.category_combo)
        
        # تاریخ
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("تاریخ:", self.date_input)
        
        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("توضیحات اختیاری...")
        form.addRow("توضیحات:", self.description_input)
        
        layout.addLayout(form)
        
        # دکمه‌ها
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_expense)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_expense(self):
        """ذخیره هزینه"""
        title = self.title_input.text().strip()
        amount = self.amount_input.value()
        description = self.description_input.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "خطا", "لطفاً عنوان را وارد کنید")
            return
        
        if amount <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً مبلغ را وارد کنید")
            return
        
        # نقشه دسته‌ها
        category_map = {
            "اجاره": "rent",
            "قبوض": "bills",
            "حقوق": "salary",
            "خرید": "purchase",
            "تعمیرات": "repairs",
            "بازاریابی": "marketing",
            "سایر": "other"
        }
        category = category_map.get(self.category_combo.currentText(), "other")
        date = self.date_input.date().toString("yyyy-MM-dd")
        
        try:
            self.db.execute_update(
                """INSERT INTO expenses (title, amount, category, date, description, created_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (title, amount, category, date, description, self.user['id'])
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره: {str(e)}")
