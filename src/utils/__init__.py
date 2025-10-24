"""Utilities package initializer.

این فایل به‌صورت امن هر دو مجموعه‌ی ابزار را در دسترس قرار می‌دهد:
- مجموعه‌ی قدیمی: helpers, export  (توابع تاریخ جلالی، قسط‌بندی، اکسپورت)
- مجموعه‌ی جدید: persian_utils, notification_manager, sms_manager, report_generator
"""

# یک لیست پویا از نمادهایی که واقعاً موجودند می‌سازیم
__all__ = []

def _export_if_present(name: str):
    """اگر نماد در فضای global هست، به __all__ اضافه‌اش کن تا از بیرون import شود."""
    if name in globals():
        __all__.append(name)

# -------- مجموعه‌ی قدیمی (اختیاری) --------
try:
    from .helpers import (
        jalali_to_gregorian,
        gregorian_to_jalali,
        get_current_jalali_date,
        add_months_to_jalali_date,
        generate_installments,
        format_currency as _format_currency_basic,
        is_date_in_range,
        compare_dates,
    )
    for _n in [
        "jalali_to_gregorian", "gregorian_to_jalali", "get_current_jalali_date",
        "add_months_to_jalali_date", "generate_installments",
        "is_date_in_range", "compare_dates"
    ]:
        _export_if_present(_n)
except Exception:
    # اگر helpers فعلاً وجود نداشت، شکست خاموش؛ پروژه down نمی‌آید
    pass

try:
    from .export import (
        export_to_excel,
        export_to_pdf,
        export_policies_to_excel,
        export_policies_to_pdf,
        export_installments_to_excel,
        export_installments_to_pdf,
    )
    for _n in [
        "export_to_excel", "export_to_pdf",
        "export_policies_to_excel", "export_policies_to_pdf",
        "export_installments_to_excel", "export_installments_to_pdf",
    ]:
        _export_if_present(_n)
except Exception:
    pass

# -------- مجموعه‌ی جدید (ترجیح داده‌شده) --------
try:
    from .persian_utils import (
        PersianDateConverter,
        format_persian_number,
        format_currency as _format_currency_persian,
    )
    for _n in ["PersianDateConverter", "format_persian_number"]:
        _export_if_present(_n)
except Exception:
    _format_currency_persian = None  # برای انتخاب تابع currency پایین لازم است

try:
    from .notification_manager import NotificationManager
    _export_if_present("NotificationManager")
except Exception:
    pass

try:
    from .sms_manager import SMSManager
    _export_if_present("SMSManager")
except Exception:
    pass

try:
    from .report_generator import ReportGenerator
    _export_if_present("ReportGenerator")
except Exception:
    pass

# -------- یکپارچه‌سازی format_currency --------
# اگر نسخه‌ی جدید موجود بود، همان را صادر کن؛ وگرنه نسخه‌ی قدیمی.
if "_format_currency_persian" in globals() and _format_currency_persian:
    format_currency = _format_currency_persian
else:
    # اگر هیچ‌کدام نبود، یک fallback خیلی ساده تعریف کن تا importها نشکنند
    if "_format_currency_basic" in globals():
        format_currency = _format_currency_basic
    else:
        def format_currency(value):
            return f"{value:,}"

_export_if_present("format_currency")
