#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
کاگان ERP - اجرای سریع
فقط اجرا کنید: python run.py

⚠️ هشدار امنیتی: این فایل برای دمو و تست سریع طراحی شده است.
برای استفاده در محیط تولید (production):
- از رمزهای هش شده استفاده کنید
- احراز هویت JWT اضافه کنید
- به جای 0.0.0.0 از 127.0.0.1 استفاده کنید
- HTTPS راه‌اندازی کنید
"""

import subprocess
import sys

# نصب خودکار وابستگیها
def install_packages():
    packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'jinja2', 'python-multipart']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"در حال نصب {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])

install_packages()

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import uvicorn
import os

# تنظیمات
DATABASE_URL = "sqlite:///./kagan.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============ مدلهای دیتابیس ============

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    full_name = Column(String(100))
    role = Column(String(20))  # admin, barber, barista
    commission_percentage = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    loyalty_points = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(50))
    inventory_type = Column(String(20))  # cafe, barbershop
    item_type = Column(String(20))  # raw_material, consumable, retail
    unit = Column(String(20))
    quantity = Column(Float, default=0)
    min_stock_alert = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Float)
    duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(50))
    category = Column(String(50))
    price = Column(Float)
    is_active = Column(Boolean, default=True)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    invoice_type = Column(String(20))  # cafe, barbershop, mixed
    total_amount = Column(Float)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float)
    payment_method = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# ============ ساخت دیتابیس ============

def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # اگر کاربر admin نیست، دادههای اولیه را اضافه کن
    if not db.query(User).filter(User.username == "admin").first():
        # کاربران
        users = [
            User(username="admin", password="admin123", full_name="مدیر سیستم", role="admin"),
            User(username="barber1", password="barber123", full_name="آرایشگر ۱", role="barber", commission_percentage=30),
            User(username="barista1", password="barista123", full_name="باریستا ۱", role="barista"),
        ]
        db.add_all(users)
        
        # مشتریان نمونه
        customers = [
            Customer(name="علی محمدی", phone="09121234567", loyalty_points=50),
            Customer(name="رضا احمدی", phone="09129876543", loyalty_points=30),
        ]
        db.add_all(customers)
        
        # انبار کافه
        cafe_items = [
            InventoryItem(name="شیر", code="CAF-001", inventory_type="cafe", item_type="raw_material", unit="لیتر", quantity=20, min_stock_alert=5, unit_price=50000),
            InventoryItem(name="قهوه", code="CAF-002", inventory_type="cafe", item_type="raw_material", unit="کیلوگرم", quantity=5, min_stock_alert=1, unit_price=800000),
        ]
        db.add_all(cafe_items)
        
        # انبار آرایشگاه
        barbershop_items = [
            InventoryItem(name="شامپو", code="BAR-001", inventory_type="barbershop", item_type="consumable", unit="لیتر", quantity=10, min_stock_alert=2, unit_price=200000),
            InventoryItem(name="رنگ مو", code="BAR-002", inventory_type="barbershop", item_type="consumable", unit="میلیلیتر", quantity=500, min_stock_alert=100, unit_price=5000),
            InventoryItem(name="واکس مو", code="BAR-003", inventory_type="barbershop", item_type="retail", unit="عدد", quantity=20, min_stock_alert=5, unit_price=150000),
        ]
        db.add_all(barbershop_items)
        
        # خدمات آرایشگاه
        services = [
            Service(name="اصلاح مو", category="haircut", price=150000, duration_minutes=30),
            Service(name="اصلاح ریش", category="haircut", price=80000, duration_minutes=15),
            Service(name="رنگ مو", category="coloring", price=300000, duration_minutes=90),
            Service(name="ماساژ سر", category="massage", price=100000, duration_minutes=20),
        ]
        db.add_all(services)
        
        # محصولات کافه
        products = [
            Product(name="اسپرسو", code="PROD-001", category="coffee", price=40000),
            Product(name="کاپوچینو", code="PROD-002", category="coffee", price=55000),
            Product(name="لاته", code="PROD-003", category="coffee", price=60000),
            Product(name="چای", code="PROD-004", category="tea", price=25000),
        ]
        db.add_all(products)
        
        db.commit()
        print("✅ دادههای اولیه اضافه شد")
    
    db.close()

# ============ FastAPI App ============

app = FastAPI(title="کاگان ERP", description="سیستم مدیریت آرایشگاه و کافه")

# صفحه اصلی با HTML فارسی
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>کاگان ERP</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Vazir', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
            .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
            .card:hover { transform: translateY(-5px); transition: 0.3s; }
            h1, h2, h3, h4, h5, p, span { color: white; }
            .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="text-center mb-5">
                <h1 class="display-3 fw-bold">🏪 کاگان ERP</h1>
                <p class="lead">سیستم جامع مدیریت آرایشگاه و کافه</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">💇</div>
                        <h4>آرایشگاه</h4>
                        <p>مدیریت خدمات، نوبتدهی و کمیسیون</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">☕</div>
                        <h4>کافه</h4>
                        <p>منوی هوشمند و فروش سریع</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">📦</div>
                        <h4>انبارداری</h4>
                        <p>مدیریت موجودی و هشدار اتمام</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">👥</div>
                        <h4>مشتریان</h4>
                        <p>CRM و باشگاه وفاداری</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">📊</div>
                        <h4>گزارشات</h4>
                        <p>سود، فروش و تراز مالی</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 p-4 text-center">
                        <div class="feature-icon">🔐</div>
                        <h4>امنیت</h4>
                        <p>سطوح دسترسی کاربران</p>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-5">
                <a href="/docs" class="btn btn-lg btn-primary me-2">📚 مستندات API</a>
                <a href="/api/customers" class="btn btn-lg btn-outline-light">👥 مشتریان</a>
            </div>
            
            <div class="text-center mt-4">
                <p class="text-muted">نام کاربری: admin | رمز: admin123</p>
            </div>
        </div>
    </body>
    </html>
    """

# API های ساده
@app.get("/api/customers")
def get_customers():
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    return customers

@app.get("/api/inventory")
def get_inventory():
    db = SessionLocal()
    items = db.query(InventoryItem).all()
    db.close()
    return items

@app.get("/api/services")
def get_services():
    db = SessionLocal()
    services = db.query(Service).all()
    db.close()
    return services

@app.get("/api/products")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    stats = {
        "customers": db.query(Customer).count(),
        "inventory_items": db.query(InventoryItem).count(),
        "services": db.query(Service).count(),
        "products": db.query(Product).count(),
        "invoices": db.query(Invoice).count(),
    }
    db.close()
    return stats

# ============ اجرا ============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏪 کاگان ERP - سیستم مدیریت آرایشگاه و کافه")
    print("="*50 + "\n")
    
    print("🔧 در حال آمادهسازی...")
    init_database()
    print("✅ دیتابیس آماده است")
    
    print("\n" + "-"*50)
    print("🚀 سرور در حال اجرا...")
    print("🌐 آدرس: http://localhost:8000")
    print("📚 مستندات: http://localhost:8000/docs")
    print("-"*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
