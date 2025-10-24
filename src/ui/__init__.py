"""UI Components"""
from .login_dialog import LoginDialog
from .main_window import MainWindow
from .dashboard_widget import DashboardWidget
from .policy_widget import PolicyWidget
from .installment_widget import InstallmentWidget
from .calendar_widget import CalendarWidget
from .reports_widget import ReportsWidget
from .sms_widget import SMSWidget
from .archive import ArchiveWidget
from .settings import SettingsWidget
__all__ = [
    'LoginDialog',
    'MainWindow',
    'DashboardWidget',
    'PolicyWidget',
    'InstallmentWidget',
    'CalendarWidget',
    'ReportsWidget',
    'SettingsWidget' ,
    'ArchiveWidget',
    'SMSWidget'
  
]
