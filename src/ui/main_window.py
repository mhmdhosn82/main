"""Main application window with tabbed interface"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                            QLabel, QToolBar, QSplitter, QPushButton, QHBoxLayout,
                            QListWidget, QListWidgetItem, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
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
        
        # Apply modern stylesheet to main window
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e8ecf1);
            }
        """)
        
        # Create central widget with splitter (sidebar + tabs)
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        
        # Create tabs widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 8px;
                background: white;
                margin-right: 5px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #d5dbdf);
                color: #2c3e50;
                padding: 12px 25px;
                margin: 2px;
                border: 2px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-color: #2980b9;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
                color: white;
            }
        """)
        
        # Create tab widgets
        from .dashboard_widget import DashboardWidget
        from .policy_widget import PolicyWidget
        from .installment_widget import InstallmentWidget
        from .overdue_installments_widget import OverdueInstallmentsWidget
        from .calendar_widget import CalendarWidget
        from .reports_widget import ReportsWidget
        from .sms_widget import SMSWidget
        
        self.dashboard = DashboardWidget(self.user, self.session)
        self.policy_widget = PolicyWidget(self.user, self.session)
        self.installment_widget = InstallmentWidget(self.user, self.session)
        self.overdue_widget = OverdueInstallmentsWidget(self.user, self.session)
        self.calendar_widget = CalendarWidget(self.user, self.session)
        self.reports_widget = ReportsWidget(self.user, self.session)
        self.sms_widget = SMSWidget(self.user, self.session)
        
        # Add tabs
        self.tabs.addTab(self.dashboard, "📊 داشبورد")
        self.tabs.addTab(self.policy_widget, "📋 بیمه‌نامه‌ها")
        self.tabs.addTab(self.installment_widget, "💰 اقساط")
        self.tabs.addTab(self.overdue_widget, "⚠️ اقساط معوق")
        self.tabs.addTab(self.calendar_widget, "📅 تقویم اقساط")
        self.tabs.addTab(self.reports_widget, "📈 گزارش‌ها")
        self.tabs.addTab(self.sms_widget, "📱 پیامک‌ها")
        
        # Connect tab changes to sidebar
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Add sidebar and tabs to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.tabs, stretch=1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("آماده")
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
    
    def create_sidebar(self):
        """Create modern sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setMaximumWidth(220)
        sidebar.setMinimumWidth(220)
        sidebar.setLayoutDirection(Qt.RightToLeft)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-left: 3px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)
        
        # App title in sidebar
        title_label = QLabel("سیستم مدیریت\nاقساط بیمه")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 15px;
                background: rgba(52, 152, 219, 0.3);
                border-radius: 5px;
                margin: 0px 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.sidebar_buttons = []
        nav_items = [
            ("📊", "داشبورد", 0),
            ("📋", "بیمه‌نامه‌ها", 1),
            ("💰", "اقساط", 2),
            ("⚠️", "اقساط معوق", 3),
            ("📅", "تقویم اقساط", 4),
            ("📈", "گزارش‌ها", 5),
            ("📱", "پیامک‌ها", 6),
        ]
        
        for icon, label, index in nav_items:
            btn = self.create_sidebar_button(icon, label, index)
            self.sidebar_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # User info at bottom
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 152, 219, 0.2);
                border-radius: 5px;
                margin: 0px 10px;
                padding: 10px;
            }
        """)
        user_layout = QVBoxLayout()
        
        user_label = QLabel(f"👤 {self.user.full_name}")
        user_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        user_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(user_label)
        
        user_frame.setLayout(user_layout)
        layout.addWidget(user_frame)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_sidebar_button(self, icon, text, tab_index):
        """Create a styled sidebar button"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setLayoutDirection(Qt.RightToLeft)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                text-align: right;
                padding: 15px 20px;
                border: none;
                border-radius: 5px;
                font-size: 11pt;
                margin: 0px 10px;
                qproperty-layoutDirection: RightToLeft;
            }
            QPushButton:hover {
                background: rgba(52, 152, 219, 0.3);
            }
            QPushButton:pressed {
                background: rgba(52, 152, 219, 0.5);
            }
        """)
        btn.clicked.connect(lambda: self.switch_to_tab(tab_index))
        return btn
    
    def switch_to_tab(self, index):
        """Switch to the specified tab"""
        self.tabs.setCurrentIndex(index)
        self.update_sidebar_selection(index)
    
    def update_sidebar_selection(self, index):
        """Update sidebar button selection state"""
        for i, btn in enumerate(self.sidebar_buttons):
            if i == index:
                btn.setLayoutDirection(Qt.RightToLeft)
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #3498db, stop:1 #2ecc71);
                        color: white;
                        text-align: right;
                        padding: 15px 20px;
                        border: none;
                        border-radius: 5px;
                        font-size: 11pt;
                        font-weight: bold;
                        margin: 0px 10px;
                        qproperty-layoutDirection: RightToLeft;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2ecc71, stop:1 #3498db);
                    }
                """)
            else:
                btn.setLayoutDirection(Qt.RightToLeft)
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: white;
                        text-align: right;
                        padding: 15px 20px;
                        border: none;
                        border-radius: 5px;
                        font-size: 11pt;
                        margin: 0px 10px;
                        qproperty-layoutDirection: RightToLeft;
                    }
                    QPushButton:hover {
                        background: rgba(52, 152, 219, 0.3);
                    }
                    QPushButton:pressed {
                        background: rgba(52, 152, 219, 0.5);
                    }
                """)
    
    def on_tab_changed(self, index):
        """Handle tab change event"""
        self.update_sidebar_selection(index)
    
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ecf0f1, stop:1 #d5dbdf);
                padding: 8px;
                spacing: 8px;
                border-bottom: 2px solid #3498db;
            }
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 10px 18px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
                border: 2px solid #2980b9;
            }
            QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
                border: 2px solid #3498db;
            }
            QToolButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
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
            self.overdue_widget.refresh()
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
