"""Calendar widget for installments"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, QLabel,
                            QListWidget, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextCharFormat, QColor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CalendarWidget(QWidget):
    """Calendar view for installments"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.installments_by_date = {}
        self.setup_ui()
        self.load_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("تقویم اقساط")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        content_layout = QHBoxLayout()
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setLayoutDirection(Qt.LeftToRight)
        self.calendar.clicked.connect(self.date_selected)
        content_layout.addWidget(self.calendar)
        
        # Details panel
        details_layout = QVBoxLayout()
        
        self.selected_date_label = QLabel("تاریخ انتخابی:")
        self.selected_date_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self.selected_date_label)
        
        self.installments_list = QListWidget()
        self.installments_list.setLayoutDirection(Qt.RightToLeft)
        details_layout.addWidget(self.installments_list)
        
        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        details_widget.setMinimumWidth(300)
        content_layout.addWidget(details_widget)
        
        layout.addLayout(content_layout)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(self.create_legend_item("🟢 پرداخت شده", QColor(39, 174, 96)))
        legend_layout.addWidget(self.create_legend_item("🟡 در انتظار", QColor(243, 156, 18)))
        legend_layout.addWidget(self.create_legend_item("🔴 معوق", QColor(231, 76, 60)))
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        self.setLayout(layout)
    
    def create_legend_item(self, text, color):
        """Create legend item"""
        label = QLabel(text)
        label.setStyleSheet(f"padding: 5px; margin: 5px;")
        return label
    
    def load_installments(self):
        """Load installments and mark calendar"""
        from ..controllers import InstallmentController
        from ..models import InsurancePolicy, Installment
        
        try:
            # Get all installments
            installments = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(InsurancePolicy.user_id == self.user.id).all()
            
            # Group by date
            self.installments_by_date = {}
            
            for inst, policy in installments:
                date_key = inst.due_date.date()
                if date_key not in self.installments_by_date:
                    self.installments_by_date[date_key] = []
                self.installments_by_date[date_key].append((inst, policy))
            
            # Mark dates on calendar
            self.mark_calendar_dates()
            
        except Exception as e:
            logger.error(f"Error loading installments: {e}")
    
    def mark_calendar_dates(self):
        """Mark dates with installments on calendar"""
        for date, installments in self.installments_by_date.items():
            qdate = QDate(date.year, date.month, date.day)
            
            # Determine color based on status
            has_paid = any(inst.status == 'paid' for inst, _ in installments)
            has_overdue = any(inst.status == 'overdue' for inst, _ in installments)
            has_pending = any(inst.status == 'pending' for inst, _ in installments)
            
            fmt = QTextCharFormat()
            fmt.setFontWeight(75)
            
            if has_overdue:
                fmt.setBackground(QColor(231, 76, 60, 100))
            elif has_pending:
                fmt.setBackground(QColor(243, 156, 18, 100))
            elif has_paid:
                fmt.setBackground(QColor(39, 174, 96, 100))
            
            self.calendar.setDateTextFormat(qdate, fmt)
    
    def date_selected(self, qdate):
        """Handle date selection"""
        from ..utils.persian_utils import format_currency
        
        date = qdate.toPyDate()
        
        # Update label
        persian_date = f"{date.year}/{date.month:02d}/{date.day:02d}"
        self.selected_date_label.setText(f"تاریخ انتخابی: {persian_date}")
        
        # Clear list
        self.installments_list.clear()
        
        # Show installments for this date
        if date in self.installments_by_date:
            for inst, policy in self.installments_by_date[date]:
                item_text = (
                    f"بیمه‌نامه {policy.policy_number} - "
                    f"قسط {inst.installment_number} - "
                    f"{format_currency(inst.amount)} - "
                    f"وضعیت: {inst.status}"
                )
                self.installments_list.addItem(item_text)
        else:
            self.installments_list.addItem("قسطی برای این تاریخ ثبت نشده است")
    
    def refresh(self):
        """Refresh calendar"""
        self.load_installments()
