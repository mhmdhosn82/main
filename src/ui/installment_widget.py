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
        
        title = QLabel("مدیریت اقساط")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "بیمه‌نامه", "قسط", "مبلغ", "سررسید", "تاریخ پرداخت", "وضعیت", "عملیات"
        ])
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_installments(self):
        """Load installments"""
        from ..controllers import InstallmentController
        from ..models import InsurancePolicy
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        try:
            controller = InstallmentController(self.session)
            
            # Get all installments for user's policies
            from ..models import Installment
            installments = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(InsurancePolicy.user_id == self.user.id).all()
            
            self.table.setRowCount(len(installments))
            
            for row, (inst, policy) in enumerate(installments):
                self.table.setItem(row, 0, QTableWidgetItem(policy.policy_number))
                self.table.setItem(row, 1, QTableWidgetItem(str(inst.installment_number)))
                self.table.setItem(row, 2, QTableWidgetItem(format_currency(inst.amount)))
                self.table.setItem(row, 3, QTableWidgetItem(
                    PersianDateConverter.gregorian_to_jalali(inst.due_date)
                ))
                payment_date = PersianDateConverter.gregorian_to_jalali(inst.payment_date) if inst.payment_date else "-"
                self.table.setItem(row, 4, QTableWidgetItem(payment_date))
                self.table.setItem(row, 5, QTableWidgetItem(inst.status))
                
                # Action button
                if inst.status == 'pending':
                    btn = QPushButton("ثبت پرداخت")
                    btn.clicked.connect(lambda checked, i=inst: self.mark_paid(i))
                    self.table.setCellWidget(row, 6, btn)
            
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
            else:
                QMessageBox.warning(self, "خطا", message)
    
    def show_payment_dialog(self):
        """Show payment dialog for quick access"""
        QMessageBox.information(self, "اطلاعات", "لطفاً قسط مورد نظر را از جدول انتخاب کنید")
    
    def refresh(self):
        """Refresh table"""
        self.load_installments()
