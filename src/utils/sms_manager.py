"""SMS manager for sending reminders via SMS API"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSManager:
    """Manage SMS reminders through API integration"""
    
    def __init__(self, api_key=None, api_url=None):
        """
        Initialize SMS manager with API credentials
        
        Args:
            api_key: API key for SMS service
            api_url: Base URL for SMS API
        """
        # Try to load from config if not provided
        if api_key is None or api_url is None:
            try:
                from .config_manager import get_config
                config = get_config()
                sms_config = config.get_sms_config()
                self.api_key = api_key or sms_config.get('api_key', '')
                self.api_url = api_url or sms_config.get('api_url', '')
                self.sender_number = sms_config.get('sender_number', '')
            except Exception as e:
                logger.warning(f"Failed to load SMS config: {e}")
                self.api_key = api_key or ""
                self.api_url = api_url or ""
                self.sender_number = ""
        else:
            self.api_key = api_key
            self.api_url = api_url
            self.sender_number = ""
        
        self.enabled = bool(self.api_key and self.api_url)
    
    def configure(self, api_key, api_url):
        """Configure SMS API settings"""
        self.api_key = api_key
        self.api_url = api_url
        self.enabled = bool(api_key and api_url)
    
    def send_sms(self, phone_number, message):
        """
        Send SMS message
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            
        Returns:
            tuple: (success: bool, response: dict)
        """
        if not self.enabled:
            logger.warning("SMS service not configured")
            return False, {"error": "SMS service not configured"}
        
        try:
            # Generic SMS API request structure
            # This should be customized based on actual SMS provider
            payload = {
                'api_key': self.api_key,
                'to': phone_number,
                'message': message
            }
            
            response = requests.post(
                f"{self.api_url}/send",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {phone_number}")
                return True, response.json()
            else:
                logger.error(f"SMS send failed: {response.status_code}")
                return False, {"error": f"HTTP {response.status_code}"}
                
        except requests.RequestException as e:
            logger.error(f"SMS request failed: {e}")
            return False, {"error": str(e)}
    
    def send_installment_reminder(self, phone_number, policy_number, amount, due_date):
        """Send installment reminder SMS"""
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        persian_date = PersianDateConverter.gregorian_to_jalali(due_date)
        message = (
            f"یادآوری پرداخت قسط\n"
            f"بیمه‌نامه: {policy_number}\n"
            f"مبلغ: {format_currency(amount)}\n"
            f"سررسید: {persian_date}"
        )
        
        return self.send_sms(phone_number, message)
    
    def send_overdue_reminder(self, phone_number, policy_number, days_overdue):
        """Send overdue payment reminder SMS"""
        message = (
            f"هشدار! قسط معوق\n"
            f"بیمه‌نامه: {policy_number}\n"
            f"{days_overdue} روز از سررسید گذشته است\n"
            f"لطفاً در اسرع وقت پرداخت نمایید"
        )
        
        return self.send_sms(phone_number, message)
    
    def send_bulk_sms(self, recipients):
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of tuples (phone_number, message)
            
        Returns:
            dict: Results with success/failure counts
        """
        results = {
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for phone_number, message in recipients:
            success, response = self.send_sms(phone_number, message)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            results['details'].append({
                'phone': phone_number,
                'success': success,
                'response': response
            })
        
        return results
