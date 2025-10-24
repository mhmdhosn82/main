"""
Dashboard widget for displaying statistics and quick actions.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from src.database.db import Database
from src.models.repository import PolicyRepository, InstallmentRepository
from src.utils.helpers import get_current_jalali_date, compare_dates


class DashboardWidget(QWidget):
    """Dashboard widget showing statistics and quick actions."""
    
    navigate_to_policies = pyqtSignal()
    navigate_to_reminders = pyqtSignal()
    
    def __init__(self, db: Database):
        """
        Initialize the dashboard widget.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.installment_repo = InstallmentRepository(db)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("داشبورد")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)
        
        # Statistics cards
        stats_layout = QGridLayout()
        layout.addLayout(stats_layout)
        
        self.total_policies_card = self.create_stat_card("تعداد کل بیمه‌نامه‌ها", "0", "#3498db")
        self.total_installments_card = self.create_stat_card("تعداد کل اقساط", "0", "#2ecc71")
        self.paid_installments_card = self.create_stat_card("اقساط پرداخت شده", "0", "#27ae60")
        self.unpaid_installments_card = self.create_stat_card("اقساط پرداخت نشده", "0", "#e74c3c")
        
        stats_layout.addWidget(self.total_policies_card, 0, 0)
        stats_layout.addWidget(self.total_installments_card, 0, 1)
        stats_layout.addWidget(self.paid_installments_card, 1, 0)
        stats_layout.addWidget(self.unpaid_installments_card, 1, 1)
        
        # Quick actions
        quick_actions_label = QLabel("دسترسی سریع")
        quick_actions_label.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px; margin-top: 20px;")
        quick_actions_label.setAlignment(Qt.AlignRight)
        layout.addWidget(quick_actions_label)
        
        actions_layout = QHBoxLayout()
        layout.addLayout(actions_layout)
        
        new_policy_btn = QPushButton("ثبت بیمه‌نامه جدید")
        new_policy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px;
                font-size: 12pt;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_policy_btn.clicked.connect(self.navigate_to_policies.emit)
        actions_layout.addWidget(new_policy_btn)
        
        view_reminders_btn = QPushButton("مشاهده یادآوری‌ها")
        view_reminders_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 15px;
                font-size: 12pt;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        view_reminders_btn.clicked.connect(self.navigate_to_reminders.emit)
        actions_layout.addWidget(view_reminders_btn)
        
        # Upcoming reminders
        reminders_label = QLabel("اقساط سررسید امروز و آینده")
        reminders_label.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px; margin-top: 20px;")
        reminders_label.setAlignment(Qt.AlignRight)
        layout.addWidget(reminders_label)
        
        self.reminders_table = QTableWidget()
        self.reminders_table.setColumnCount(5)
        self.reminders_table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "نام بیمه‌شده", "شماره قسط", "تاریخ سررسید", "مبلغ"
        ])
        self.reminders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.reminders_table.setAlternatingRowColors(True)
        self.reminders_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.reminders_table)
        
        layout.addStretch()
        
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """
        Create a statistics card.
        
        Args:
            title: Card title
            value: Card value
            color: Card color
            
        Returns:
            Statistics card widget
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        card.setLayout(layout)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 28pt; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12pt;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Store reference to value label for updating
        card.value_label = value_label
        
        return card
    
    def refresh_data(self):
        """Refresh dashboard data."""
        # Get statistics
        stats = self.policy_repo.get_statistics()
        
        # Update cards
        self.total_policies_card.value_label.setText(str(stats['total_policies']))
        self.total_installments_card.value_label.setText(str(stats['total_installments']))
        self.paid_installments_card.value_label.setText(str(stats['paid_installments']))
        self.unpaid_installments_card.value_label.setText(str(stats['unpaid_installments']))
        
        # Load upcoming reminders
        self.load_reminders()
    
    def load_reminders(self):
        """Load upcoming reminders."""
        current_date = get_current_jalali_date()
        
        # Get all unpaid installments
        installments = self.installment_repo.get_due_installments()
        
        # Filter for today and future dates
        upcoming = []
        for inst in installments:
            if compare_dates(inst['due_date'], current_date) >= 0:
                upcoming.append(inst)
        
        # Sort by due date
        upcoming.sort(key=lambda x: x['due_date'])
        
        # Display in table (limit to 10)
        self.reminders_table.setRowCount(0)
        for i, inst in enumerate(upcoming[:10]):
            self.reminders_table.insertRow(i)
            self.reminders_table.setItem(i, 0, QTableWidgetItem(inst['policy_number']))
            self.reminders_table.setItem(i, 1, QTableWidgetItem(inst['insured_name']))
            self.reminders_table.setItem(i, 2, QTableWidgetItem(str(inst['installment_number'])))
            self.reminders_table.setItem(i, 3, QTableWidgetItem(inst['due_date']))
            self.reminders_table.setItem(i, 4, QTableWidgetItem(f"{inst['amount']:,.0f} ریال"))
