"""Main application window with tabbed interface"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                            QLabel, QToolBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.apply_vazir_font()
        self.setup_reminder_timer()
        
    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle(f"سیستم مدیریت اقساط بیمه ایران - {self.user.full_name}")
        self.setMinimumSize(1200, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Create central widget with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d6eaf8;
            }
        """)
        
        # Create tab widgets
        from .dashboard_widget import DashboardWidget
        from .policy_widget import PolicyWidget
        from .installment_widget import InstallmentWidget
        from .calendar_widget import CalendarWidget
        from .reports_widget import ReportsWidget
        from .sms_widget import SMSWidget
        
        self.dashboard = DashboardWidget(self.user, self.session)
        self.policy_widget = PolicyWidget(self.user, self.session)
        self.installment_widget = InstallmentWidget(self.user, self.session)
        self.calendar_widget = CalendarWidget(self.user, self.session)
        self.reports_widget = ReportsWidget(self.user, self.session)
        self.sms_widget = SMSWidget(self.user, self.session)
        
        # Add tabs
        self.tabs.addTab(self.dashboard, "📊 داشبورد")
        self.tabs.addTab(self.policy_widget, "📋 بیمه‌نامه‌ها")
        self.tabs.addTab(self.installment_widget, "💰 اقساط")
        self.tabs.addTab(self.calendar_widget, "📅 تقویم اقساط")
        self.tabs.addTab(self.reports_widget, "📈 گزارش‌ها")
        self.tabs.addTab(self.sms_widget, "📱 پیامک‌ها")
        
        self.setCentralWidget(self.tabs)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("آماده")
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("فایل")
        
        refresh_action = QAction("بروزرسانی", self)
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("تنظیمات")
        
        sms_settings_action = QAction("تنظیمات پیامک", self)
        sms_settings_action.triggered.connect(self.show_sms_settings)
        settings_menu.addAction(sms_settings_action)
        
        profile_action = QAction("پروفایل کاربری", self)
        profile_action.triggered.connect(self.show_profile)
        settings_menu.addAction(profile_action)
        
        # Help menu
        help_menu = menubar.addMenu("راهنما")
        
        about_action = QAction("درباره", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ecf0f1;
                padding: 5px;
                spacing: 5px;
            }
            QToolButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Refresh action
        refresh_action = QAction("🔄 بروزرسانی", self)
        refresh_action.triggered.connect(self.refresh_all)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Quick actions
        add_policy_action = QAction("➕ بیمه‌نامه جدید", self)
        add_policy_action.triggered.connect(self.quick_add_policy)
        toolbar.addAction(add_policy_action)
        
        add_installment_action = QAction("💰 ثبت پرداخت", self)
        add_installment_action.triggered.connect(self.quick_add_payment)
        toolbar.addAction(add_installment_action)
        
        self.addToolBar(toolbar)
    
    def apply_vazir_font(self):
        """Apply Vazir font for better Persian text display"""
        # Try to load Vazir font, fallback to system default
        try:
            font = QFont("Vazir", 10)
            self.setFont(font)
        except:
            # Fallback to a common Persian-supporting font
            font = QFont("Tahoma", 10)
            self.setFont(font)
            logger.warning("Vazir font not found, using Tahoma as fallback")
    
    def setup_reminder_timer(self):
        """Setup timer for checking reminders"""
        from ..controllers import ReminderController
        
        self.reminder_controller = ReminderController(self.session)
        
        # Check reminders every 5 minutes
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(300000)  # 5 minutes in milliseconds
        
        # Check immediately on startup
        QTimer.singleShot(5000, self.check_reminders)  # Wait 5 seconds after startup
    
    def check_reminders(self):
        """Check and process pending reminders"""
        try:
            stats = self.reminder_controller.process_pending_reminders()
            if stats['sent'] > 0:
                logger.info(f"Sent {stats['sent']} reminders")
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
    
    def refresh_all(self):
        """Refresh all widgets"""
        try:
            self.dashboard.refresh()
            self.policy_widget.refresh()
            self.installment_widget.refresh()
            self.calendar_widget.refresh()
            self.statusBar.showMessage("بروزرسانی انجام شد", 3000)
        except Exception as e:
            logger.error(f"Error refreshing: {e}")
            QMessageBox.warning(self, "خطا", "خطا در بروزرسانی")
    
    def quick_add_policy(self):
        """Quick add policy dialog"""
        self.tabs.setCurrentWidget(self.policy_widget)
        self.policy_widget.show_add_policy_dialog()
    
    def quick_add_payment(self):
        """Quick add payment dialog"""
        self.tabs.setCurrentWidget(self.installment_widget)
        self.installment_widget.show_payment_dialog()
    
    def show_sms_settings(self):
        """Show SMS settings dialog"""
        from .sms_settings_dialog import SMSSettingsDialog
        dialog = SMSSettingsDialog(self.session, self)
        dialog.exec_()
    
    def show_profile(self):
        """Show user profile"""
        QMessageBox.information(
            self,
            "پروفایل کاربری",
            f"نام کاربری: {self.user.username}\n"
            f"نام: {self.user.full_name}\n"
            f"ایمیل: {self.user.email or 'ثبت نشده'}\n"
            f"تلفن: {self.user.phone or 'ثبت نشده'}"
        )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "درباره سیستم",
            "<h3>سیستم مدیریت اقساط بیمه ایران</h3>"
            "<p>نسخه 1.0.0</p>"
            "<p>سیستم جامع مدیریت اقساط بیمه‌نامه‌ها</p>"
            "<p>ویژگی‌ها:</p>"
            "<ul>"
            "<li>مدیریت بیمه‌نامه‌ها و اقساط</li>"
            "<li>تقویم شمسی و یادآورهای هوشمند</li>"
            "<li>گزارش‌گیری پیشرفته</li>"
            "<li>ارسال پیامک یادآوری</li>"
            "<li>نمایش نمودارهای آماری</li>"
            "</ul>"
            "<p>© 2024 تمام حقوق محفوظ است</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            'خروج از برنامه',
            'آیا مطمئن هستید که می‌خواهید خارج شوید؟',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
