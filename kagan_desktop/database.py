"""
مدیریت دیتابیس SQLite
"""
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """کلاس مدیریت دیتابیس SQLite"""
    
    def __init__(self, db_path: str = "kagan_desktop.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """دریافت اتصال به دیتابیس"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize(self):
        """ایجاد جداول و داده‌های اولیه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول کاربران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                commission_percentage REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول مشتریان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                birth_date TEXT,
                notes TEXT,
                loyalty_points INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول انبار
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                inventory_type TEXT NOT NULL,
                item_type TEXT NOT NULL,
                unit TEXT NOT NULL,
                quantity REAL DEFAULT 0,
                min_stock_alert REAL DEFAULT 0,
                unit_price REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول خدمات آرایشگاه
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                duration_minutes INTEGER DEFAULT 30,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول BOM خدمات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_bom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                inventory_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (service_id) REFERENCES services(id),
                FOREIGN KEY (inventory_id) REFERENCES inventory(id)
            )
        """)
        
        # جدول محصولات کافه
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول Recipe محصولات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_recipe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                inventory_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (inventory_id) REFERENCES inventory(id)
            )
        """)
        
        # جدول نوبت‌دهی
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                barber_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                booking_datetime TEXT NOT NULL,
                status TEXT DEFAULT 'reserved',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (barber_id) REFERENCES users(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        """)
        
        # جدول فاکتورها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                user_id INTEGER NOT NULL,
                invoice_type TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT DEFAULT 'paid',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # جدول آیتم‌های فاکتور
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                barber_id INTEGER,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (barber_id) REFERENCES users(id)
            )
        """)
        
        # جدول تنظیمات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        conn.commit()
        
        # ایجاد کاربران پیشفرض
        self._create_default_users()
        self._create_sample_data()
    
    def _create_default_users(self):
        """ایجاد کاربران پیشفرض"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        default_users = [
            ("admin", "admin123", "مدیر سیستم", "admin", 0),
            ("barber1", "barber123", "آرایشگر اول", "barber", 30),
            ("barista1", "barista123", "باریستا اول", "barista", 0),
        ]
        
        for username, password, full_name, role, commission in default_users:
            # بررسی وجود کاربر
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is None:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password, full_name, role, commission_percentage)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password_hash, full_name, role, commission))
        
        conn.commit()
    
    def _create_sample_data(self):
        """ایجاد داده‌های نمونه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # مشتریان نمونه
        sample_customers = [
            ("علی احمدی", "09123456789", "ali@example.com", None, "مشتری وفادار"),
            ("سارا محمدی", "09124567890", None, None, "ترجیح: رنگ روشن"),
        ]
        
        for name, phone, email, birth_date, notes in sample_customers:
            cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO customers (name, phone, email, birth_date, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, phone, email, birth_date, notes))
        
        # کالاهای انبار نمونه
        sample_inventory = [
            ("شیر", "CAF-001", "cafe", "raw_material", "liter", 10.0, 2.0, 50000),
            ("قهوه", "CAF-002", "cafe", "raw_material", "kg", 5.0, 1.0, 500000),
            ("شکلات", "CAF-003", "cafe", "raw_material", "kg", 3.0, 0.5, 300000),
            ("شامپو", "BAR-001", "barbershop", "consumable", "ml", 2000, 500, 150),
            ("رنگ مو", "BAR-002", "barbershop", "consumable", "ml", 1000, 200, 300),
            ("اکسیدان", "BAR-003", "barbershop", "consumable", "ml", 1000, 200, 200),
            ("واکس مو", "BAR-004", "barbershop", "product", "unit", 20, 5, 50000),
        ]
        
        for name, code, inv_type, item_type, unit, qty, min_stock, price in sample_inventory:
            cursor.execute("SELECT id FROM inventory WHERE code = ?", (code,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO inventory (name, code, inventory_type, item_type, unit, quantity, min_stock_alert, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, code, inv_type, item_type, unit, qty, min_stock, price))
        
        # خدمات آرایشگاه نمونه
        sample_services = [
            ("اصلاح", "haircut", 200000, 30, "اصلاح مو و ریش"),
            ("گریم صورت", "facial", 150000, 45, "گریم و پاکسازی صورت"),
            ("رنگ مو", "coloring", 300000, 90, "رنگ کامل مو"),
            ("ماساژ سر", "massage", 100000, 20, "ماساژ آرامش‌بخش"),
        ]
        
        for name, category, price, duration, desc in sample_services:
            cursor.execute("SELECT id FROM services WHERE name = ? AND category = ?", (name, category))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO services (name, category, price, duration_minutes, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, category, price, duration, desc))
        
        # محصولات کافه نمونه
        sample_products = [
            ("اسپرسو", "PROD-001", "coffee", 30000, "قهوه تک شات"),
            ("کاپوچینو", "PROD-002", "coffee", 50000, "قهوه با شیر و فوم"),
            ("هات چاکلت", "PROD-003", "chocolate", 45000, "شکلات داغ"),
        ]
        
        for name, code, category, price, desc in sample_products:
            cursor.execute("SELECT id FROM products WHERE code = ?", (code,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO products (name, code, category, price, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, code, category, price, desc))
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """اجرای کوئری SELECT"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """اجرای کوئری INSERT/UPDATE/DELETE"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    
    def close(self):
        """بستن اتصال"""
        if self.conn:
            self.conn.close()
            self.conn = None
