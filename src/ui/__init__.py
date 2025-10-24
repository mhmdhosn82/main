"""UI Components"""
from .login_dialog import LoginDialog
from .register_dialog import RegisterDialog
from .main_window import MainWindow
from .dashboard_widget import DashboardWidget
from .policy_widget import PolicyWidget
from .installment_widget import InstallmentWidget
from .calendar_widget import CalendarWidget
from .reports_widget import ReportsWidget
from .sms_widget import SMSWidget
from .sms_settings_dialog import SMSSettingsDialog

__all__ = [
    'LoginDialog',
    'RegisterDialog',
    'MainWindow',
    'DashboardWidget',
    'PolicyWidget',
    'InstallmentWidget',
    'CalendarWidget',
    'ReportsWidget',
    'SMSWidget',
    'SMSSettingsDialog'
]
