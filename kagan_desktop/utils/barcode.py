"""
بارکد اسکنر و تولید بارکد
"""
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
from typing import Optional, Dict
from PyQt6.QtGui import QPixmap


class BarcodeHandler:
    """کلاس مدیریت بارکد"""
    
    def __init__(self):
        self.barcode_format = "ean13"  # پیشفرض: EAN-13
        
    def generate_barcode(self, code: str, barcode_type: str = "code128") -> Optional[bytes]:
        """
        تولید بارکد
        
        Args:
            code: کد برای تولید بارکد
            barcode_type: نوع بارکد (code128, ean13, ean8, upca, etc.)
        
        Returns:
            تصویر بارکد به صورت bytes یا None در صورت خطا
        """
        try:
            # انتخاب کلاس بارکد
            barcode_class = barcode.get_barcode_class(barcode_type)
            
            # ایجاد بارکد
            barcode_instance = barcode_class(code, writer=ImageWriter())
            
            # رندر کردن به buffer
            buffer = io.BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.3,
                'module_height': 10.0,
                'quiet_zone': 5.0,
                'font_size': 10,
                'text_distance': 3.0,
            })
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"خطا در تولید بارکد: {e}")
            return None
    
    def generate_barcode_pixmap(self, code: str, barcode_type: str = "code128") -> Optional[QPixmap]:
        """
        تولید بارکد به صورت QPixmap برای نمایش در Qt
        
        Args:
            code: کد برای تولید بارکد
            barcode_type: نوع بارکد
        
        Returns:
            QPixmap یا None در صورت خطا
        """
        barcode_bytes = self.generate_barcode(code, barcode_type)
        
        if barcode_bytes:
            pixmap = QPixmap()
            pixmap.loadFromData(barcode_bytes)
            return pixmap
        
        return None
    
    def save_barcode_image(self, code: str, filename: str, barcode_type: str = "code128") -> bool:
        """
        ذخیره تصویر بارکد در فایل
        
        Args:
            code: کد برای تولید بارکد
            filename: نام فایل خروجی
            barcode_type: نوع بارکد
        
        Returns:
            True در صورت موفقیت
        """
        try:
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_instance = barcode_class(code, writer=ImageWriter())
            
            # ذخیره در فایل
            barcode_instance.save(filename, options={
                'module_width': 0.3,
                'module_height': 10.0,
                'quiet_zone': 5.0,
                'font_size': 10,
                'text_distance': 3.0,
            })
            
            return True
        except Exception as e:
            print(f"خطا در ذخیره بارکد: {e}")
            return False
    
    def validate_barcode(self, code: str, barcode_type: str = "code128") -> bool:
        """
        اعتبارسنجی کد بارکد
        
        Args:
            code: کد برای بررسی
            barcode_type: نوع بارکد
        
        Returns:
            True اگر کد معتبر باشد
        """
        try:
            barcode_class = barcode.get_barcode_class(barcode_type)
            # تلاش برای ایجاد بارکد
            barcode_class(code)
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> list:
        """لیست فرمت‌های پشتیبانی شده"""
        return [
            'code128',
            'code39',
            'ean13',
            'ean8',
            'jan',
            'isbn10',
            'isbn13',
            'issn',
            'upca',
            'ean',
            'pzn',
        ]


class BarcodeScanner:
    """کلاس مدیریت اسکنر بارکد USB"""
    
    def __init__(self):
        self.last_scanned = ""
        self.scan_callback = None
        
    def set_scan_callback(self, callback):
        """
        تنظیم تابع callback برای زمانی که بارکد اسکن می‌شود
        
        Args:
            callback: تابعی که با کد اسکن شده فراخوانی می‌شود
        """
        self.scan_callback = callback
    
    def process_scan(self, scanned_data: str):
        """
        پردازش داده اسکن شده
        
        Args:
            scanned_data: داده دریافتی از اسکنر
        """
        # پاکسازی داده
        scanned_data = scanned_data.strip()
        
        if not scanned_data:
            return
        
        self.last_scanned = scanned_data
        
        # اگر callback تنظیم شده باشد، آن را فراخوانی کن
        if self.scan_callback:
            self.scan_callback(scanned_data)
    
    def get_last_scanned(self) -> str:
        """دریافت آخرین کد اسکن شده"""
        return self.last_scanned
    
    def clear_last_scanned(self):
        """پاک کردن آخرین کد اسکن شده"""
        self.last_scanned = ""


# نمونه استفاده:
# 
# barcode_handler = BarcodeHandler()
# 
# # تولید بارکد
# barcode_bytes = barcode_handler.generate_barcode("1234567890", "code128")
# 
# # نمایش در Qt
# pixmap = barcode_handler.generate_barcode_pixmap("1234567890")
# label.setPixmap(pixmap)
# 
# # ذخیره در فایل
# barcode_handler.save_barcode_image("1234567890", "barcode.png")
# 
# # اسکنر
# scanner = BarcodeScanner()
# scanner.set_scan_callback(lambda code: print(f"Scanned: {code}"))
