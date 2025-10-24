"""Desktop notification manager"""
from plyer import notification
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manage desktop notifications"""
    
    def __init__(self):
        self.app_name = "Iran Insurance Manager"
        self.app_icon = None  # Can be set to icon path
    
    def send_notification(self, title, message, timeout=10):
        """Send a desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout
            )
            logger.info(f"Notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def send_installment_reminder(self, policy_number, amount, due_date):
        """Send installment reminder notification"""
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        title = "یادآوری پرداخت قسط"
        persian_date = PersianDateConverter.gregorian_to_jalali(due_date)
        message = f"قسط بیمه‌نامه {policy_number}\nمبلغ: {format_currency(amount)}\nسررسید: {persian_date}"
        
        return self.send_notification(title, message)
    
    def send_overdue_reminder(self, policy_number, days_overdue):
        """Send overdue payment notification"""
        title = "هشدار! قسط معوق"
        message = f"بیمه‌نامه {policy_number}\n{days_overdue} روز از سررسید گذشته است"
        
        return self.send_notification(title, message, timeout=15)
    
    def send_payment_confirmation(self, policy_number, amount):
        """Send payment confirmation notification"""
        from ..utils.persian_utils import format_currency
        
        title = "پرداخت موفق"
        message = f"قسط بیمه‌نامه {policy_number}\nمبلغ {format_currency(amount)} پرداخت شد"
        
        return self.send_notification(title, message)
