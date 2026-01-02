# Kagan ERP System

سیستم ERP جامع برای مدیریت کسبوکار ترکیبی آرایشگاه و کافه

![Kagan ERP](https://github.com/user-attachments/assets/debb2c5d-443f-4406-a41c-7f9ce2be8991)

## ویژگی‌های اصلی

### ۱. انبارداری دوگانه (Dual Inventory)
- **انبار کافه**: مواد اولیه (شیر، قهوه، شکلات) با واحد گرم/لیتر
- **انبار آرایشگاه**: مواد مصرفی (شامپو، رنگ، اکسیدان) و محصولات ویترینی (واکس مو، ادکلن)
- **سیستم BOM/فرمولاسیون**: اتصال خودکار خدمات به مواد مصرفی
- **هشدار خودکار**: نوتیفیکیشن در صورت رسیدن به حداقل موجودی
- کسر خودکار موجودی پس از هر فروش

### ۲. بخش آرایشگاه
- تعریف خدمات مختلف (اصلاح، گریم، ماساژ، رنگ مو)
- مدیریت آرایشگران و تعیین درصد کمیسیون
- سیستم نوبت‌دهی (Booking) با مدیریت تقویم
- گزارش کمیسیون روزانه/ماهانه برای هر آرایشگر
- فاکتورزنی ترکیبی (خدمت + فروش کالا)

### ۳. بخش کافه
- منوی هوشمند با Recipe برای هر محصول
- رابط POS برای فروش سریع
- کسر خودکار مواد اولیه بر اساس دستور پخت (Recipe)
- دسته‌بندی محصولات (قهوه، چای، دسر)

### ۴. سیستم مشتریان (CRM)
- پرونده الکترونیک مشتری با تاریخچه کامل
- ثبت اطلاعات تماس و یادداشت‌ها
- سوابق خدمات و پرداخت‌ها
- باشگاه وفاداری با امتیازدهی خودکار (۱ امتیاز به ازای هر ۱۰,۰۰۰ ریال)
- آمادگی برای اتصال به پنل پیامک

### ۵. مدیریت مالی
- گزارش سود خالص
- محاسبه موجودی ریالی انبار
- تراز مالی
- گزارش فروش روزانه/ماهانه
- تفکیک فروش بر اساس نوع (آرایشگاه/کافه)

### ۶. امنیت و سطح دسترسی
- نقش‌های مختلف: ادمین، آرایشگر، باریستا
- محدودسازی دسترسی به API بر اساس نقش
- احراز هویت JWT-based
- رمزنگاری امن پسوردها با bcrypt

## تکنولوژی‌های استفاده شده

- **Backend**: Python 3.9+ با FastAPI
- **Database**: SQLAlchemy ORM با SQLite (قابل تغییر به PostgreSQL)
- **Authentication**: JWT با python-jose
- **Password Hashing**: bcrypt
- **Frontend**: HTML/CSS/JavaScript با Bootstrap RTL
- **Font**: Vazir (فونت فارسی)

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.9 یا بالاتر
- pip

### مراحل نصب

1. **کلون کردن پروژه**:
```bash
git clone https://github.com/mhmdhosn821/Kagan.git
cd Kagan
```

2. **نصب وابستگی‌ها**:
```bash
pip install -r requirements.txt
```

3. **ایجاد فایل تنظیمات**:
```bash
cp .env.example .env
```

4. **ویرایش فایل `.env`** و تنظیم پارامترها (در صورت نیاز):
```env
DATABASE_URL=sqlite:///./kagan.db
SECRET_KEY=your-secret-key-here
```

5. **مقداردهی اولیه دیتابیس**:
```bash
python init_db.py
```

این دستور دیتابیس را ایجاد و کاربران و داده‌های نمونه زیر را اضافه می‌کند:
- **Admin**: username=`admin`, password=`admin123`
- **Barber**: username=`barber1`, password=`barber123`
- **Barista**: username=`barista1`, password=`barista123`

6. **اجرای برنامه**:
```bash
python app/main.py
```

یا با uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **دسترسی به برنامه**:
- صفحه اصلی: http://localhost:8000
- مستندات API (Swagger): http://localhost:8000/docs
- مستندات جایگزین (ReDoc): http://localhost:8000/redoc

## استفاده از API

### ثبت نام کاربر جدید
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "email": "user@example.com",
    "full_name": "کاربر تستی",
    "password": "pass123",
    "role": "barber",
    "commission_percentage": 30
  }'
```

### ورود به سیستم
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

پاسخ:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

### دریافت لیست مشتریان
```bash
curl -X GET "http://localhost:8000/customers/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### افزودن کالا به انبار
```bash
curl -X POST "http://localhost:8000/inventory/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "شیر",
    "code": "CAF-001",
    "inventory_type": "cafe",
    "item_type": "raw_material",
    "unit": "liter",
    "min_stock_alert": 2.0,
    "unit_price": 50000
  }'
```

### ایجاد فاکتور
```bash
curl -X POST "http://localhost:8000/invoices/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "invoice_type": "cafe",
    "items": [
      {
        "item_type": "product",
        "product_id": 1,
        "quantity": 2,
        "unit_price": 50000
      }
    ],
    "discount_amount": 0,
    "payment_method": "cash"
  }'
```

## تست سیستم

### اجرای تست‌های API
```bash
python test_api.py
```

این دستور تمام endpoint های API را تست می‌کند و نتیجه را نمایش می‌دهد.

### اجرای دمو
```bash
python demo.py
```

این اسکریپت یک سناریوی کامل از ایجاد فاکتور، کسر خودکار موجودی و محاسبه کمیسیون را نمایش می‌دهد.

## ساختار پروژه

```
kagan/
├── app/
│   ├── __init__.py
│   ├── main.py              # نقطه ورود برنامه
│   ├── config.py            # تنظیمات
│   ├── database.py          # پیکربندی دیتابیس
│   ├── models/              # مدل‌های دیتابیس
│   │   ├── user.py         # کاربران و نقش‌ها
│   │   ├── customer.py     # مشتریان
│   │   ├── inventory.py    # انبار
│   │   ├── service.py      # خدمات آرایشگاه
│   │   ├── product.py      # محصولات کافه و BOM/Recipe
│   │   ├── invoice.py      # فاکتورها
│   │   └── booking.py      # نوبت‌دهی
│   ├── routers/            # API endpoints
│   │   ├── auth.py         # احراز هویت
│   │   ├── customers.py    # مدیریت مشتریان
│   │   ├── inventory.py    # مدیریت انبار
│   │   ├── barbershop.py   # عملیات آرایشگاه
│   │   ├── cafe.py         # عملیات کافه
│   │   ├── invoices.py     # فاکتورزنی
│   │   └── reports.py      # گزارشات
│   ├── services/           # لاجیک کسب‌وکار
│   │   ├── auth.py         # سرویس احراز هویت
│   │   └── inventory.py    # سرویس انبارداری
│   └── templates/          # قالب‌های HTML
│       └── index.html      # صفحه خانه
├── static/
│   ├── css/
│   │   └── style.css       # استایل‌های سفارشی
│   ├── js/
│   └── fonts/
├── init_db.py              # اسکریپت مقداردهی اولیه
├── test_api.py             # تست‌های API
├── demo.py                 # اسکریپت دمو
├── requirements.txt        # وابستگی‌های پایتون
├── .env.example            # نمونه فایل تنظیمات
├── .gitignore
└── README.md
```

## نمونه‌های استفاده

### ۱. ایجاد یک خدمت آرایشگاه با BOM
```python
# 1. ایجاد خدمت رنگ مو
POST /barbershop/services
{
  "name": "رنگ مو",
  "category": "coloring",
  "price": 300000,
  "duration_minutes": 90
}

# 2. افزودن مواد مصرفی به BOM
POST /barbershop/services/{service_id}/bom
{
  "inventory_item_id": 1,  # رنگ مو
  "quantity": 50  # 50ml
}

POST /barbershop/services/{service_id}/bom
{
  "inventory_item_id": 2,  # اکسیدان
  "quantity": 50  # 50ml
}
```

### ۲. ایجاد محصول کافه با Recipe
```python
# 1. ایجاد محصول
POST /cafe/products
{
  "name": "کاپوچینو",
  "code": "PROD-002",
  "price": 50000,
  "category": "coffee"
}

# 2. افزودن دستور پخت
POST /cafe/products/{product_id}/recipe
{
  "inventory_item_id": 1,  # شیر
  "quantity": 0.15  # 150ml
}

POST /cafe/products/{product_id}/recipe
{
  "inventory_item_id": 2,  # قهوه
  "quantity": 0.02  # 20g
}
```

### ۳. ثبت نوبت آرایشگاه
```python
POST /barbershop/bookings
{
  "customer_id": 1,
  "barber_id": 2,
  "service_id": 1,
  "booking_datetime": "2024-01-15T10:00:00",
  "notes": "مشتری حساسیت به رنگ دارد"
}
```

## API Endpoints

### Authentication
- `POST /auth/register` - ثبت نام کاربر جدید
- `POST /auth/login` - ورود به سیستم
- `GET /auth/me` - دریافت اطلاعات کاربر جاری

### Customers
- `GET /customers/` - لیست مشتریان
- `POST /customers/` - افزودن مشتری
- `GET /customers/{id}` - دریافت اطلاعات مشتری
- `PUT /customers/{id}` - ویرایش مشتری
- `POST /customers/{id}/loyalty` - افزودن امتیاز وفاداری

### Inventory
- `GET /inventory/` - لیست کالاهای انبار
- `POST /inventory/` - افزودن کالا به انبار
- `GET /inventory/{id}` - دریافت اطلاعات کالا
- `PUT /inventory/{id}` - ویرایش کالا
- `POST /inventory/{id}/add-stock` - افزودن موجودی
- `GET /inventory/alerts` - هشدارهای موجودی
- `GET /inventory/value` - ارزش کل انبار

### Barbershop
- `GET /barbershop/services` - لیست خدمات
- `POST /barbershop/services` - افزودن خدمت
- `GET /barbershop/services/{id}` - دریافت اطلاعات خدمت
- `POST /barbershop/services/{id}/bom` - افزودن BOM
- `GET /barbershop/bookings` - لیست نوبت‌ها
- `POST /barbershop/bookings` - ثبت نوبت
- `PUT /barbershop/bookings/{id}/status` - تغییر وضعیت نوبت
- `GET /barbershop/barbers` - لیست آرایشگران

### Cafe
- `GET /cafe/products` - لیست محصولات
- `POST /cafe/products` - افزودن محصول
- `GET /cafe/products/{id}` - دریافت اطلاعات محصول
- `POST /cafe/products/{id}/recipe` - افزودن Recipe
- `GET /cafe/menu` - منوی دسته‌بندی شده

### Invoices
- `GET /invoices/` - لیست فاکتورها
- `POST /invoices/` - ایجاد فاکتور (با کسر خودکار موجودی)
- `GET /invoices/{id}` - دریافت جزئیات فاکتور

### Reports
- `GET /reports/dashboard` - داشبورد خلاصه
- `GET /reports/sales` - گزارش فروش
- `GET /reports/commission` - گزارش کمیسیون
- `GET /reports/inventory-usage` - گزارش مصرف انبار
- `GET /reports/profit` - گزارش سود

## توسعه و مشارکت

برای مشارکت در توسعه این پروژه:

1. Fork کنید
2. یک branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push به branch (`git push origin feature/amazing-feature`)
5. یک Pull Request باز کنید

## مجوز

این پروژه برای استفاده شخصی و تجاری آزاد است.

## پشتیبانی

در صورت بروز مشکل یا سوال، یک Issue در GitHub باز کنید.

## توسعه‌دهنده

توسعه یافته با ❤️ برای کسب‌وکار کاگان

---

**نکته**: این سیستم برای محیط production نیاز به تنظیمات امنیتی بیشتر، استفاده از PostgreSQL و راه‌اندازی HTTPS دارد.