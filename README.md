# Kagan ERP System

سیستم ERP جامع برای مدیریت کسبوکار ترکیبی آرایشگاه و کافه

## ویژگی‌های اصلی

### ۱. انبارداری دوگانه (Dual Inventory)
- انبار کافه: مواد اولیه (شیر، قهوه، شکلات) با واحد گرم/سیسی
- انبار آرایشگاه: مواد مصرفی (شامپو، رنگ، اکسیدان) و محصولات ویترینی (واکس مو، ادکلن)
- سیستم BOM/فرمولاسیون: اتصال خدمات به مواد مصرفی
- هشدار خودکار اتمام موجودی

### ۲. بخش آرایشگاه
- تعریف خدمات مختلف (اصلاح، گریم، ماساژ، رنگ)
- مدیریت آرایشگران و درصد کمیسیون
- سیستم نوبت‌دهی (Booking)
- گزارش کمیسیون روزانه/ماهانه

### ۳. بخش کافه
- منوی هوشمند با Recipe
- رابط POS برای فروش سریع
- کسر خودکار مواد اولیه

### ۴. سیستم مشتریان (CRM)
- پرونده الکترونیک مشتری
- سوابق خدمات و پرداخت‌ها
- باشگاه وفاداری با امتیازدهی

### ۵. مدیریت مالی
- گزارش سود خالص
- موجودی ریالی انبار
- تراز مالی
- چاپ فاکتور

### ۶. امنیت
- نقش‌ها: ادمین، آرایشگر، باریستا
- محدودسازی دسترسی بر اساس نقش

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.9+
- pip

### مراحل نصب

1. نصب وابستگی‌ها:
```bash
pip install -r requirements.txt
```

2. ایجاد فایل `.env` از روی `.env.example`:
```bash
cp .env.example .env
```

3. ویرایش فایل `.env` و تنظیم پارامترها

4. اجرای برنامه:
```bash
python app/main.py
```

یا با uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. دسترسی به برنامه:
- وب اپلیکیشن: http://localhost:8000
- مستندات API: http://localhost:8000/docs

## ساختار پروژه

```
kagan/
├── app/
│   ├── main.py              # نقطه ورود برنامه
│   ├── config.py            # تنظیمات
│   ├── database.py          # پیکربندی دیتابیس
│   ├── models/              # مدل‌های دیتابیس
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── inventory.py
│   │   ├── service.py
│   │   ├── product.py
│   │   ├── invoice.py
│   │   └── booking.py
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── inventory.py
│   │   ├── barbershop.py
│   │   ├── cafe.py
│   │   ├── invoices.py
│   │   └── reports.py
│   ├── services/            # لاجیک کسب‌وکار
│   │   ├── auth.py
│   │   └── inventory.py
│   └── templates/           # قالب‌های HTML
├── static/
│   ├── css/
│   ├── js/
│   └── fonts/
├── requirements.txt
├── .env.example
└── README.md
```

## استفاده از API

### ثبت نام کاربر اولیه (ادمین)
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@kagan.local",
    "full_name": "مدیر سیستم",
    "password": "admin123",
    "role": "admin"
  }'
```

### ورود به سیستم
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

برای اطلاعات بیشتر درباره APIها به مستندات خودکار Swagger مراجعه کنید:
http://localhost:8000/docs

## تکنولوژی‌های استفاده شده

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy ORM با SQLite
- **Authentication**: JWT با python-jose
- **Frontend**: HTML/CSS/JavaScript با Bootstrap RTL
- **Font**: Vazir (فونت فارسی)

## مجوز

این پروژه برای استفاده شخصی و تجاری آزاد است.

## توسعه‌دهنده

توسعه یافته با ❤️ برای کسب‌وکار کاگان