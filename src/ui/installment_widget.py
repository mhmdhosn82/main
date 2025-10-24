"""Installment management widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class InstallmentWidget(QWidget):
    """Installment management interface"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.load_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title
        header_layout = QHBoxLayout()
        title = QLabel("یادآورهای اقساط سررسید")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("اقساطی که در 30 روز آینده سررسید دارند:")
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Table with reminder fields
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "نوع بیمه", "مبلغ قسط", "تاریخ سررسید", 
            "شماره موبایل", "نام بیمه‌گذار", "عملیات"
        ])
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_installments(self):
        """Load upcoming installments (reminder view)"""
        from ..controllers import InstallmentController
        from ..models import InsurancePolicy
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        try:
            controller = InstallmentController(self.session)
            
            # Get upcoming installments in next 30 days
            from ..models import Installment
            from datetime import datetime, timedelta
            
            today = datetime.now()
            future_date = today + timedelta(days=30)
            
            installments = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(
                InsurancePolicy.user_id == self.user.id,
                Installment.due_date >= today,
                Installment.due_date <= future_date,
                Installment.status.in_(['pending', 'overdue'])
            ).order_by(Installment.due_date).all()
            
            self.table.setRowCount(len(installments))
            
            for row, (inst, policy) in enumerate(installments):
                # Policy Number
                self.table.setItem(row, 0, QTableWidgetItem(policy.policy_number))
                
                # Insurance Type
                self.table.setItem(row, 1, QTableWidgetItem(policy.policy_type or "-"))
                
                # Due Amount
                self.table.setItem(row, 2, QTableWidgetItem(format_currency(inst.amount)))
                
                # Due Date
                self.table.setItem(row, 3, QTableWidgetItem(
                    PersianDateConverter.gregorian_to_jalali(inst.due_date)
                ))
                
                # Mobile Number
                self.table.setItem(row, 4, QTableWidgetItem(policy.mobile_number or "-"))
                
                # Policy Holder Name
                self.table.setItem(row, 5, QTableWidgetItem(policy.policy_holder_name))
                
                # Action button
                if inst.status in ['pending', 'overdue']:
                    btn = QPushButton("ثبت پرداخت")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover { background-color: #229954; }
                    """)
                    btn.clicked.connect(lambda checked, i=inst: self.mark_paid(i))
                    self.table.setCellWidget(row, 6, btn)
                else:
                    self.table.setItem(row, 6, QTableWidgetItem(""))
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error loading installments: {e}")
    
    def mark_paid(self, installment):
        """Mark installment as paid"""
        from ..controllers import InstallmentController
        
        reply = QMessageBox.question(
            self,
            'تأیید پرداخت',
            f'آیا پرداخت قسط {installment.installment_number} را تأیید می‌کنید؟',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            controller = InstallmentController(self.session)
            success, message = controller.mark_as_paid(installment.id)
            
            if success:
                QMessageBox.information(self, "موفق", message)
                self.load_installments()
                
                # Refresh other widgets in the main window if available
                parent_window = self.window()
                if hasattr(parent_window, 'calendar_widget'):
                    try:
                        parent_window.calendar_widget.refresh()
                    except Exception as e:
                        logger.warning(f"Could not refresh calendar: {e}")
                if hasattr(parent_window, 'dashboard'):
                    try:
                        parent_window.dashboard.refresh()
                    except Exception as e:
                        logger.warning(f"Could not refresh dashboard: {e}")
            else:
                QMessageBox.warning(self, "خطا", message)
    
    def show_payment_dialog(self):
        """Show payment dialog for quick access"""
        QMessageBox.information(self, "اطلاعات", "لطفاً قسط مورد نظر را از جدول انتخاب کنید")
    
    def refresh(self):
        """Refresh table"""
        self.load_installments()
