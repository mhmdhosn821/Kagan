"""
اتصال به API پیامک
"""
import requests
from typing import Optional, Dict, List
from datetime import datetime


class SMSApi:
    """کلاس اتصال به سرویس پیامک"""
    
    def __init__(self):
        self.api_key = ""
        self.api_url = ""
        self.sender_number = ""
        self.provider = "kavenegar"  # kavenegar, melipayamak, etc.
        
    def configure(self, api_key: str, sender_number: str, provider: str = "kavenegar"):
        """تنظیم اطلاعات API"""
        self.api_key = api_key
        self.sender_number = sender_number
        self.provider = provider
        
        # تنظیم URL بر اساس ارائه‌دهنده
        if provider == "kavenegar":
            self.api_url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
        elif provider == "melipayamak":
            self.api_url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
        
    def send_sms(self, phone: str, message: str) -> Dict:
        """
        ارسال پیامک تکی
        
        Args:
            phone: شماره موبایل
            message: متن پیامک
        
        Returns:
            نتیجه ارسال
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "API تنظیم نشده است"
            }
        
        try:
            if self.provider == "kavenegar":
                response = requests.post(
                    self.api_url,
                    data={
                        "sender": self.sender_number,
                        "receptor": phone,
                        "message": message
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "پیامک با موفقیت ارسال شد",
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "message": f"خطا: {response.status_code}"
                    }
            
            elif self.provider == "melipayamak":
                response = requests.post(
                    self.api_url,
                    json={
                        "username": self.api_key,
                        "password": self.sender_number,
                        "to": phone,
                        "from": self.sender_number,
                        "text": message,
                        "isFlash": False
                    },
                    timeout=10
                )
                
                result = response.json()
                if result.get("RetStatus") == 1:
                    return {
                        "success": True,
                        "message": "پیامک با موفقیت ارسال شد",
                        "data": result
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("StrRetStatus", "خطای نامشخص")
                    }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "زمان اتصال به سرور پیامک تمام شد"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"خطا در ارسال پیامک: {str(e)}"
            }
    
    def send_welcome_sms(self, phone: str, customer_name: str) -> Dict:
        """ارسال پیامک خوشآمدگویی"""
        message = f"""
سلام {customer_name} عزیز
به خانواده کاگان خوش آمدید!
🎉 امیدواریم تجربه خوبی از خدمات ما داشته باشید.
        """.strip()
        return self.send_sms(phone, message)
    
    def send_appointment_reminder(self, phone: str, customer_name: str, 
                                 datetime_str: str, service_name: str) -> Dict:
        """ارسال یادآوری نوبت"""
        message = f"""
{customer_name} عزیز، یادآوری نوبت شما
⏰ زمان: {datetime_str}
📋 خدمت: {service_name}
📍 کاگان - منتظر شما هستیم
        """.strip()
        return self.send_sms(phone, message)
    
    def send_birthday_greeting(self, phone: str, customer_name: str) -> Dict:
        """ارسال تبریک تولد"""
        message = f"""
🎂 {customer_name} عزیز
تولدت مبارک!
🎉 آرزوی سلامتی و شادکامی برای شما داریم
🎁 با هدیه ویژه تولد منتظر شما هستیم
کاگان
        """.strip()
        return self.send_sms(phone, message)
    
    def send_invoice_link(self, phone: str, customer_name: str, 
                        invoice_number: str, amount: int) -> Dict:
        """ارسال لینک فاکتور"""
        message = f"""
{customer_name} عزیز
فاکتور شما ثبت شد
شماره: {invoice_number}
مبلغ: {amount:,} ریال
از خرید شما متشکریم 🙏
کاگان
        """.strip()
        return self.send_sms(phone, message)
    
    def send_bulk_sms(self, recipients: List[Dict[str, str]]) -> Dict:
        """
        ارسال انبوه پیامک
        
        Args:
            recipients: لیست دیکشنری شامل phone و message
        
        Returns:
            نتیجه ارسال کلی
        """
        results = {
            "total": len(recipients),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for recipient in recipients:
            phone = recipient.get("phone")
            message = recipient.get("message")
            
            if not phone or not message:
                results["failed"] += 1
                continue
            
            result = self.send_sms(phone, message)
            
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "phone": phone,
                    "error": result.get("message")
                })
        
        return results
    
    def get_credit_balance(self) -> Optional[float]:
        """دریافت اعتبار باقیمانده"""
        # پیاده‌سازی بر اساس API provider
        # این قابلیت در آینده اضافه خواهد شد
        return None
