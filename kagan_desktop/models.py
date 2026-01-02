"""
مدل‌های داده برای اپلیکیشن
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """مدل کاربر"""
    id: int
    username: str
    full_name: str
    role: str
    commission_percentage: float = 0.0
    is_active: bool = True
    
    @property
    def role_display(self) -> str:
        """نمایش نقش به فارسی"""
        roles = {
            "admin": "مدیر",
            "barber": "آرایشگر",
            "barista": "باریستا"
        }
        return roles.get(self.role, self.role)


@dataclass
class Customer:
    """مدل مشتری"""
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[str] = None
    notes: Optional[str] = None
    loyalty_points: int = 0
    created_at: Optional[str] = None


@dataclass
class InventoryItem:
    """مدل کالای انبار"""
    id: int
    name: str
    code: str
    inventory_type: str
    item_type: str
    unit: str
    quantity: float = 0.0
    min_stock_alert: float = 0.0
    unit_price: float = 0.0
    created_at: Optional[str] = None
    
    @property
    def inventory_type_display(self) -> str:
        """نمایش نوع انبار به فارسی"""
        types = {
            "cafe": "کافه",
            "barbershop": "آرایشگاه"
        }
        return types.get(self.inventory_type, self.inventory_type)
    
    @property
    def item_type_display(self) -> str:
        """نمایش نوع کالا به فارسی"""
        types = {
            "raw_material": "مواد اولیه",
            "consumable": "مواد مصرفی",
            "product": "محصول"
        }
        return types.get(self.item_type, self.item_type)
    
    @property
    def unit_display(self) -> str:
        """نمایش واحد به فارسی"""
        units = {
            "liter": "لیتر",
            "kg": "کیلوگرم",
            "gram": "گرم",
            "ml": "میلی‌لیتر",
            "unit": "عدد"
        }
        return units.get(self.unit, self.unit)
    
    @property
    def is_low_stock(self) -> bool:
        """بررسی موجودی کم"""
        return self.quantity <= self.min_stock_alert


@dataclass
class Service:
    """مدل خدمت آرایشگاه"""
    id: int
    name: str
    category: str
    price: float
    duration_minutes: int = 30
    description: Optional[str] = None
    created_at: Optional[str] = None
    
    @property
    def category_display(self) -> str:
        """نمایش دسته به فارسی"""
        categories = {
            "haircut": "اصلاح مو",
            "facial": "گریم صورت",
            "coloring": "رنگ",
            "massage": "ماساژ"
        }
        return categories.get(self.category, self.category)


@dataclass
class Product:
    """مدل محصول کافه"""
    id: int
    name: str
    code: str
    category: str
    price: float
    description: Optional[str] = None
    created_at: Optional[str] = None
    
    @property
    def category_display(self) -> str:
        """نمایش دسته به فارسی"""
        categories = {
            "coffee": "قهوه",
            "tea": "چای",
            "chocolate": "شکلات",
            "dessert": "دسر"
        }
        return categories.get(self.category, self.category)


@dataclass
class Booking:
    """مدل نوبت"""
    id: int
    customer_id: int
    barber_id: int
    service_id: int
    booking_datetime: str
    status: str = "reserved"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    
    @property
    def status_display(self) -> str:
        """نمایش وضعیت به فارسی"""
        statuses = {
            "reserved": "رزرو شده",
            "completed": "تکمیل شده",
            "cancelled": "لغو شده"
        }
        return statuses.get(self.status, self.status)


@dataclass
class Invoice:
    """مدل فاکتور"""
    id: int
    invoice_number: str
    customer_id: Optional[int]
    user_id: int
    invoice_type: str
    subtotal: float
    discount_amount: float
    total_amount: float
    payment_method: str
    status: str = "paid"
    created_at: Optional[str] = None
    
    @property
    def invoice_type_display(self) -> str:
        """نمایش نوع فاکتور به فارسی"""
        types = {
            "cafe": "کافه",
            "barbershop": "آرایشگاه",
            "mixed": "ترکیبی"
        }
        return types.get(self.invoice_type, self.invoice_type)
    
    @property
    def payment_method_display(self) -> str:
        """نمایش روش پرداخت به فارسی"""
        methods = {
            "cash": "نقدی",
            "card": "کارت",
            "credit": "اعتباری"
        }
        return methods.get(self.payment_method, self.payment_method)


@dataclass
class InvoiceItem:
    """مدل آیتم فاکتور"""
    id: int
    invoice_id: int
    item_type: str
    item_id: int
    item_name: str
    quantity: float
    unit_price: float
    total_price: float
    barber_id: Optional[int] = None
