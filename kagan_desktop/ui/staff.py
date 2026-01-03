"""
مدیریت کارکرد پرسنل
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QDateEdit, QDialog,
    QFormLayout, QDialogButtonBox, QTimeEdit, QDoubleSpinBox, QTextEdit,
    QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QDate, QTime
from database import Database
from utils.jalali import format_jalali_date, gregorian_to_jalali
from datetime import datetime, timedelta


class StaffPage(QWidget):
    """صفحه مدیریت کارکرد پرسنل"""
    
    def __init__(self, db: Database, user: dict):
        super().__init__()
        self.db = db
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("👨‍💼 مدیریت کارکرد پرسنل")
        title.setProperty("heading", "h2")
        layout.addWidget(title)
        
        # کارت‌های خلاصه
        summary_layout = QHBoxLayout()
        
        self.total_hours_card = self.create_summary_card("کل ساعات کاری", "0 ساعت", "#6366F1")
        summary_layout.addWidget(self.total_hours_card)
        
        self.overtime_card = self.create_summary_card("اضافه‌کاری", "0 ساعت", "#F59E0B")
        summary_layout.addWidget(self.overtime_card)
        
        self.staff_count_card = self.create_summary_card("تعداد پرسنل فعال", "0", "#10B981")
        summary_layout.addWidget(self.staff_count_card)
        
        layout.addLayout(summary_layout)
        
        # فیلتر و دکمه‌های عمل
        top_layout = QHBoxLayout()
        
        # انتخاب پرسنل
        top_layout.addWidget(QLabel("پرسنل:"))
        self.staff_combo = QComboBox()
        self.load_staff()
        self.staff_combo.currentTextChanged.connect(self.load_attendance)
        top_layout.addWidget(self.staff_combo)
        
        # فیلتر تاریخ
        top_layout.addWidget(QLabel("از:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.dateChanged.connect(self.load_attendance)
        top_layout.addWidget(self.from_date)
        
        top_layout.addWidget(QLabel("تا:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self.load_attendance)
        top_layout.addWidget(self.to_date)
        
        top_layout.addStretch()
        
        # دکمه افزودن
        add_btn = QPushButton("➕ ثبت حضور/غیاب")
        add_btn.setProperty("success", True)
        add_btn.clicked.connect(self.add_attendance)
        top_layout.addWidget(add_btn)
        
        layout.addLayout(top_layout)
        
        # جدول کارکرد
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(7)
        self.attendance_table.setHorizontalHeaderLabels([
            "تاریخ", "پرسنل", "ورود", "خروج", "ساعات کاری", "اضافه‌کاری", "یادداشت"
        ])
        self.attendance_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.attendance_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.attendance_table)
        
        self.setLayout(layout)
        
        # بارگذاری داده‌ها
        self.load_attendance()
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
    
    def load_staff(self):
        """بارگذاری لیست پرسنل"""
        try:
            self.staff_combo.addItem("همه پرسنل", None)
            
            staff = self.db.execute_query(
                "SELECT id, full_name FROM users WHERE is_active = 1 ORDER BY full_name",
                ()
            )
            
            for person in staff:
                self.staff_combo.addItem(person['full_name'], person['id'])
        except Exception as e:
            print(f"خطا در بارگذاری پرسنل: {e}")
    
    def load_attendance(self):
        """بارگذاری کارکرد"""
        try:
            self.attendance_table.setRowCount(0)
            
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            staff_id = self.staff_combo.currentData()
            
            # ساخت کوئری
            query = """
                SELECT sa.*, u.full_name as staff_name
                FROM staff_attendance sa
                JOIN users u ON sa.user_id = u.id
                WHERE DATE(sa.date) BETWEEN ? AND ?
            """
            params = [from_date, to_date]
            
            if staff_id:
                query += " AND sa.user_id = ?"
                params.append(staff_id)
            
            query += " ORDER BY sa.date DESC"
            
            attendance = self.db.execute_query(query, tuple(params))
            
            for record in attendance:
                row_position = self.attendance_table.rowCount()
                self.attendance_table.insertRow(row_position)
                
                # تاریخ
                att_date = datetime.fromisoformat(record['date'])
                self.attendance_table.setItem(row_position, 0,
                    QTableWidgetItem(gregorian_to_jalali(att_date)))
                
                # پرسنل
                self.attendance_table.setItem(row_position, 1,
                    QTableWidgetItem(record['staff_name']))
                
                # ورود
                check_in = record['check_in'] or "-"
                self.attendance_table.setItem(row_position, 2,
                    QTableWidgetItem(check_in))
                
                # خروج
                check_out = record['check_out'] or "-"
                self.attendance_table.setItem(row_position, 3,
                    QTableWidgetItem(check_out))
                
                # محاسبه ساعات کاری
                work_hours = self.calculate_work_hours(check_in, check_out)
                self.attendance_table.setItem(row_position, 4,
                    QTableWidgetItem(work_hours))
                
                # اضافه‌کاری
                overtime = record['overtime_hours'] or 0
                self.attendance_table.setItem(row_position, 5,
                    QTableWidgetItem(f"{overtime:.1f} ساعت"))
                
                # یادداشت
                notes = record['notes'] or "-"
                self.attendance_table.setItem(row_position, 6,
                    QTableWidgetItem(notes[:50] + "..." if len(notes) > 50 else notes))
            
            # بروزرسانی خلاصه
            self.update_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری کارکرد: {str(e)}")
    
    def calculate_work_hours(self, check_in: str, check_out: str) -> str:
        """محاسبه ساعات کاری"""
        if not check_in or not check_out or check_in == "-" or check_out == "-":
            return "-"
        
        try:
            # تبدیل به datetime
            fmt = "%H:%M" if ":" in check_in and len(check_in) == 5 else "%H:%M:%S"
            in_time = datetime.strptime(check_in, fmt)
            out_time = datetime.strptime(check_out, fmt)
            
            # محاسبه اختلاف
            delta = out_time - in_time
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            
            return f"{hours}:{minutes:02d} ساعت"
        except:
            return "-"
    
    def update_summary(self):
        """بروزرسانی کارت‌های خلاصه"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # محاسبه کل ساعات (تقریبی)
            # برای دقت بیشتر باید محاسبه دقیق‌تر انجام شود
            total_query = """
                SELECT COUNT(*) * 8 as approx_hours
                FROM staff_attendance
                WHERE DATE(date) BETWEEN ? AND ?
                AND check_in IS NOT NULL AND check_out IS NOT NULL
            """
            total_result = self.db.execute_query(total_query, (from_date, to_date))
            total_hours = total_result[0]['approx_hours'] if total_result else 0
            
            # اضافه‌کاری
            overtime_query = """
                SELECT COALESCE(SUM(overtime_hours), 0) as total
                FROM staff_attendance
                WHERE DATE(date) BETWEEN ? AND ?
            """
            overtime_result = self.db.execute_query(overtime_query, (from_date, to_date))
            overtime = overtime_result[0]['total'] if overtime_result else 0
            
            # تعداد پرسنل فعال
            staff_count_query = """
                SELECT COUNT(DISTINCT user_id) as count
                FROM staff_attendance
                WHERE DATE(date) BETWEEN ? AND ?
            """
            staff_result = self.db.execute_query(staff_count_query, (from_date, to_date))
            staff_count = staff_result[0]['count'] if staff_result else 0
            
            # بروزرسانی کارت‌ها
            hours_layout = self.total_hours_card.layout()
            hours_layout.itemAt(1).widget().setText(f"{total_hours} ساعت")
            
            overtime_layout = self.overtime_card.layout()
            overtime_layout.itemAt(1).widget().setText(f"{overtime:.1f} ساعت")
            
            count_layout = self.staff_count_card.layout()
            count_layout.itemAt(1).widget().setText(str(staff_count))
            
        except Exception as e:
            print(f"خطا در بروزرسانی خلاصه: {e}")
    
    def add_attendance(self):
        """افزودن رکورد حضور/غیاب"""
        dialog = AttendanceDialog(self.db, self.user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_attendance()


class AttendanceDialog(QDialog):
    """دیالوگ ثبت حضور/غیاب"""
    
    def __init__(self, db: Database, user: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.setWindowTitle("ثبت حضور/غیاب")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # فرم
        form = QFormLayout()
        
        # انتخاب پرسنل
        self.staff_combo = QComboBox()
        staff = self.db.execute_query(
            "SELECT id, full_name FROM users WHERE is_active = 1 ORDER BY full_name",
            ()
        )
        for person in staff:
            self.staff_combo.addItem(person['full_name'], person['id'])
        form.addRow("پرسنل:", self.staff_combo)
        
        # تاریخ
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("تاریخ:", self.date_input)
        
        # ساعت ورود
        self.check_in_input = QTimeEdit()
        self.check_in_input.setDisplayFormat("HH:mm")
        self.check_in_input.setTime(QTime(8, 0))
        form.addRow("ساعت ورود:", self.check_in_input)
        
        # ساعت خروج
        self.check_out_input = QTimeEdit()
        self.check_out_input.setDisplayFormat("HH:mm")
        self.check_out_input.setTime(QTime(16, 0))
        form.addRow("ساعت خروج:", self.check_out_input)
        
        # اضافه‌کاری
        self.overtime_input = QDoubleSpinBox()
        self.overtime_input.setMaximum(24)
        self.overtime_input.setSuffix(" ساعت")
        form.addRow("اضافه‌کاری:", self.overtime_input)
        
        # یادداشت
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("یادداشت اختیاری...")
        form.addRow("یادداشت:", self.notes_input)
        
        layout.addLayout(form)
        
        # دکمه‌ها
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_attendance)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_attendance(self):
        """ذخیره رکورد"""
        staff_id = self.staff_combo.currentData()
        date = self.date_input.date().toString("yyyy-MM-dd")
        check_in = self.check_in_input.time().toString("HH:mm")
        check_out = self.check_out_input.time().toString("HH:mm")
        overtime = self.overtime_input.value()
        notes = self.notes_input.toPlainText().strip()
        
        try:
            self.db.execute_update(
                """INSERT INTO staff_attendance 
                   (user_id, date, check_in, check_out, overtime_hours, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (staff_id, date, check_in, check_out, overtime, notes)
            )
            
            QMessageBox.information(self, "موفق", "رکورد حضور با موفقیت ثبت شد")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره: {str(e)}")
