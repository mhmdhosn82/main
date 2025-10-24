"""UI package initialization."""

from .main_window import MainWindow
from .dashboard import DashboardWidget
from .policy_management import PolicyManagementWidget
from .installment_management import InstallmentManagementWidget
from .reminders import RemindersWidget
from .archive import ArchiveWidget
from .settings import SettingsWidget

__all__ = [
    'MainWindow',
    'DashboardWidget',
    'PolicyManagementWidget',
    'InstallmentManagementWidget',
    'RemindersWidget',
    'ArchiveWidget',
    'SettingsWidget'
]
