"""
اتصال به کارتخوان (POS Terminal)
"""
import serial
import serial.tools.list_ports
from typing import Optional, Dict, List
import time


class POSConnector:
    """کلاس اتصال به کارتخوان"""
    
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.port_name = ""
        self.baudrate = 9600
        self.timeout = 30  # ثانیه
        
    def list_available_ports(self) -> List[str]:
        """لیست پورت‌های سریال موجود"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port_name: str, baudrate: int = 9600) -> Dict:
        """
        اتصال به کارتخوان
        
        Args:
            port_name: نام پورت سریال (مثلاً COM3 یا /dev/ttyUSB0)
            baudrate: سرعت ارتباط
        
        Returns:
            نتیجه اتصال
        """
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.port_name = port_name
            self.baudrate = baudrate
            
            return {
                "success": True,
                "message": f"اتصال به {port_name} برقرار شد"
            }
        except serial.SerialException as e:
            return {
                "success": False,
                "message": f"خطا در اتصال: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"خطای غیرمنتظره: {str(e)}"
            }
    
    def disconnect(self):
        """قطع اتصال"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
    
    def is_connected(self) -> bool:
        """بررسی اتصال"""
        return self.serial_port is not None and self.serial_port.is_open
    
    def send_payment_request(self, amount: int) -> Dict:
        """
        ارسال درخواست پرداخت به کارتخوان
        
        Args:
            amount: مبلغ به ریال
        
        Returns:
            نتیجه تراکنش
        """
        if not self.is_connected():
            return {
                "success": False,
                "message": "اتصال به کارتخوان برقرار نیست"
            }
        
        try:
            # فرمت پروتکل استانداری (ممکن است نیاز به تغییر داشته باشد)
            # این یک نمونه ساده است و باید بر اساس دستگاه خاص تنظیم شود
            command = f"PAY:{amount}\r\n".encode('ascii')
            
            # ارسال دستور
            self.serial_port.write(command)
            
            # انتظار برای پاسخ
            start_time = time.time()
            response_buffer = b""
            
            while time.time() - start_time < self.timeout:
                if self.serial_port.in_waiting > 0:
                    chunk = self.serial_port.read(self.serial_port.in_waiting)
                    response_buffer += chunk
                    
                    # بررسی پایان پاسخ (معمولاً با \r\n یا \n)
                    if b'\n' in response_buffer or b'\r' in response_buffer:
                        break
                
                time.sleep(0.1)
            
            # تجزیه پاسخ
            response = response_buffer.decode('ascii', errors='ignore').strip()
            
            if response.startswith("OK:"):
                # تراکنش موفق
                tracking_code = response.split(":")[1] if ":" in response else ""
                return {
                    "success": True,
                    "message": "پرداخت با موفقیت انجام شد",
                    "tracking_code": tracking_code,
                    "amount": amount
                }
            elif response.startswith("ERR:"):
                # خطا در تراکنش
                error_msg = response.split(":")[1] if ":" in response else "خطای نامشخص"
                return {
                    "success": False,
                    "message": f"تراکنش ناموفق: {error_msg}"
                }
            else:
                return {
                    "success": False,
                    "message": f"پاسخ نامعتبر: {response}"
                }
            
        except serial.SerialException as e:
            return {
                "success": False,
                "message": f"خطا در ارتباط سریال: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"خطای غیرمنتظره: {str(e)}"
            }
    
    def cancel_transaction(self) -> Dict:
        """لغو تراکنش جاری"""
        if not self.is_connected():
            return {
                "success": False,
                "message": "اتصال به کارتخوان برقرار نیست"
            }
        
        try:
            command = b"CANCEL\r\n"
            self.serial_port.write(command)
            
            return {
                "success": True,
                "message": "درخواست لغو ارسال شد"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"خطا در لغو: {str(e)}"
            }
    
    def test_connection(self) -> Dict:
        """تست اتصال"""
        if not self.is_connected():
            return {
                "success": False,
                "message": "اتصال برقرار نیست"
            }
        
        try:
            # ارسال دستور ping
            command = b"PING\r\n"
            self.serial_port.write(command)
            
            # انتظار برای پاسخ
            time.sleep(1)
            
            if self.serial_port.in_waiting > 0:
                response = self.serial_port.read(self.serial_port.in_waiting)
                return {
                    "success": True,
                    "message": "کارتخوان پاسخ می‌دهد",
                    "response": response.decode('ascii', errors='ignore')
                }
            else:
                return {
                    "success": False,
                    "message": "کارتخوان پاسخی نداد"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"خطا در تست: {str(e)}"
            }
    
    def __del__(self):
        """تمیز کردن منابع"""
        self.disconnect()
