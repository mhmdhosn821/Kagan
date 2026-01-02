"""
چاپ فاکتور
"""
from typing import Dict, List, Any
from datetime import datetime


class InvoicePrinter:
    """کلاس چاپ فاکتور"""
    
    def __init__(self, business_name: str = "کاگان"):
        self.business_name = business_name
    
    def print_invoice(self, invoice: Dict[str, Any], items: List[Dict[str, Any]]):
        """چاپ فاکتور"""
        try:
            # در اینجا می‌توانید از کتابخانه‌های چاپ استفاده کنید
            # مثل reportlab یا ارسال به پرینتر
            
            # برای الان فقط یک پیاده‌سازی ساده نمایشی
            print("=" * 50)
            print(f"{self.business_name.center(50)}")
            print("=" * 50)
            print(f"\nشماره فاکتور: {invoice['invoice_number']}")
            print(f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
            print(f"مشتری: {invoice.get('customer_name', 'مشتری عمومی')}")
            print("\n" + "-" * 50)
            print(f"{'نام':<30} {'تعداد':<10} {'قیمت':<10}")
            print("-" * 50)
            
            for item in items:
                print(f"{item['item_name']:<30} {item['quantity']:<10} {item['total_price']:,.0f}")
            
            print("-" * 50)
            print(f"جمع کل: {invoice['subtotal']:,.0f} ریال")
            print(f"تخفیف: {invoice['discount_amount']:,.0f} ریال")
            print(f"مبلغ نهایی: {invoice['total_amount']:,.0f} ریال")
            print(f"روش پرداخت: {invoice['payment_method']}")
            print("=" * 50)
            print("\nبا تشکر از خرید شما")
            print("=" * 50)
            
            return True
        except Exception as e:
            print(f"خطا در چاپ فاکتور: {str(e)}")
            return False
    
    def save_invoice_pdf(self, invoice: Dict[str, Any], items: List[Dict[str, Any]], filepath: str):
        """ذخیره فاکتور به صورت PDF"""
        try:
            # اینجا می‌توانید از reportlab استفاده کنید
            # برای ساخت PDF با فونت فارسی
            pass
        except Exception as e:
            print(f"خطا در ذخیره PDF: {str(e)}")
            return False
