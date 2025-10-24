"""Persian/Farsi utilities and Solar Hijri calendar support"""
import jdatetime
from datetime import datetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime

class PersianDateConverter:
    """Convert between Gregorian and Persian (Solar Hijri) dates"""
    
    @staticmethod
    def gregorian_to_jalali(date):
        """Convert Gregorian date to Jalali"""
        if isinstance(date, datetime):
            j = JalaliDateTime.to_jalali(date)
            return f"{j.year}/{j.month:02d}/{j.day:02d}"
        return ""
    
    @staticmethod
    def jalali_to_gregorian(year, month, day):
        """Convert Jalali date to Gregorian"""
        try:
            j = JalaliDate(year, month, day)
            g = j.to_gregorian()
            return datetime(g.year, g.month, g.day)
        except:
            return None
    
    @staticmethod
    def get_jalali_now():
        """Get current Jalali date and time"""
        return JalaliDateTime.now()
    
    @staticmethod
    def format_jalali_date(date, format_string='%Y/%m/%d'):
        """Format Jalali date"""
        if isinstance(date, datetime):
            j = JalaliDateTime.to_jalali(date)
            return j.strftime(format_string)
        return ""
    
    @staticmethod
    def get_jalali_month_name(month):
        """Get Persian month name"""
        months = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        return months.get(month, '')
    
    @staticmethod
    def get_jalali_weekday_name(date):
        """Get Persian weekday name"""
        weekdays = {
            0: 'شنبه', 1: 'یکشنبه', 2: 'دوشنبه',
            3: 'سه‌شنبه', 4: 'چهارشنبه', 5: 'پنج‌شنبه', 6: 'جمعه'
        }
        if isinstance(date, datetime):
            j = JalaliDateTime.to_jalali(date)
            return weekdays.get(j.weekday(), '')
        return ""

def format_persian_number(number):
    """Convert English numbers to Persian numbers"""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    
    str_number = str(number)
    for i in range(10):
        str_number = str_number.replace(english_digits[i], persian_digits[i])
    
    return str_number

def format_currency(amount):
    """Format amount as Persian currency (Rial)"""
    if amount is None:
        return "۰ ریال"
    
    # Format with thousand separators
    formatted = "{:,}".format(int(amount))
    formatted = format_persian_number(formatted)
    return f"{formatted} ریال"
