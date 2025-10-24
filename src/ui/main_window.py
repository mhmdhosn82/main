"""
Main window for the Insurance Management System.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QStackedWidget, QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from src.ui.dashboard import DashboardWidget
from src.ui.policy_management import PolicyManagementWidget
from src.ui.installment_management import InstallmentManagementWidget
from src.ui.reminders import RemindersWidget
from src.ui.archive import ArchiveWidget
from src.ui.settings import SettingsWidget
from src.database.db import Database


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, db: Database):
        """
        Initialize the main window.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("نرم‌افزار مدیریت اقساط بیمه ایران - حسن‌آبادی 37751")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set RTL layout
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Set font
        font = QFont("Vazir", 10)
        self.setFont(font)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Add widgets to stack
        self.dashboard_widget = DashboardWidget(self.db)
        self.policy_widget = PolicyManagementWidget(self.db)
        self.installment_widget = InstallmentManagementWidget(self.db)
        self.reminders_widget = RemindersWidget(self.db)
        self.archive_widget = ArchiveWidget(self.db)
        self.settings_widget = SettingsWidget(self.db)
        
        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.policy_widget)
        self.content_stack.addWidget(self.installment_widget)
        self.content_stack.addWidget(self.reminders_widget)
        self.content_stack.addWidget(self.archive_widget)
        self.content_stack.addWidget(self.settings_widget)
        
        # Show dashboard by default
        self.content_stack.setCurrentWidget(self.dashboard_widget)
        
        # Connect signals
        self.dashboard_widget.navigate_to_policies.connect(lambda: self.show_page(1))
        self.dashboard_widget.navigate_to_reminders.connect(lambda: self.show_page(3))
        self.policy_widget.policy_selected.connect(self.show_policy_installments)
        
    def create_sidebar(self) -> QWidget:
        """
        Create the sidebar navigation.
        
        Returns:
            Sidebar widget
        """
        sidebar = QFrame()
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 12px;
                text-align: right;
                font-size: 11pt;
                border-radius: 3px;
                margin: 3px;
            }
            QPushButton:hover {
                background-color: #3d566e;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout()
        sidebar.setLayout(layout)
        
        # Logo/Title
        title_label = QLabel("سیستم مدیریت بیمه")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 14pt; font-weight: bold; padding: 20px;")
        layout.addWidget(title_label)
        
        # Navigation buttons
        nav_buttons = [
            ("داشبورد", 0),
            ("مدیریت بیمه‌نامه‌ها", 1),
            ("مدیریت اقساط", 2),
            ("یادآوری‌ها", 3),
            ("آرشیو", 4),
            ("تنظیمات", 5),
        ]
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, idx=index: self.show_page(idx))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return sidebar
    
    def show_page(self, index: int):
        """
        Show a specific page.
        
        Args:
            index: Page index
        """
        self.content_stack.setCurrentIndex(index)
        
        # Refresh the page if needed
        if index == 0:  # Dashboard
            self.dashboard_widget.refresh_data()
        elif index == 1:  # Policy Management
            self.policy_widget.refresh_data()
        elif index == 2:  # Installment Management
            self.installment_widget.refresh_data()
        elif index == 3:  # Reminders
            self.reminders_widget.refresh_data()
        elif index == 4:  # Archive
            self.archive_widget.refresh_data()
    
    def show_policy_installments(self, policy_id: int):
        """
        Show installments for a specific policy.
        
        Args:
            policy_id: The policy ID
        """
        self.installment_widget.load_policy_installments(policy_id)
        self.content_stack.setCurrentWidget(self.installment_widget)
