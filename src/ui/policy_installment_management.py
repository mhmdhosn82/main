"""Policy installment management dialog"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QGroupBox, QFormLayout, QWidget)
from PyQt5.QtCore import Qt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PolicyInstallmentDialog(QDialog):
    """Dialog for managing installments of a specific policy"""
    
    def __init__(self, policy, session, parent=None):
        super().__init__(parent)
        self.policy = policy
        self.session = session
        self.setWindowTitle(f"مدیریت اقساط - بیمه‌نامه {policy.policy_number}")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Policy info section
        info_group = QGroupBox("اطلاعات بیمه‌نامه")
        info_layout = QFormLayout()
        
        info_layout.addRow("شماره بیمه‌نامه:", QLabel(self.policy.policy_number))
        info_layout.addRow("بیمه‌گذار:", QLabel(self.policy.policy_holder_name))
        info_layout.addRow("شماره موبایل:", QLabel(self.policy.mobile_number or "-"))
        info_layout.addRow("نوع بیمه:", QLabel(self.policy.policy_type or "-"))
        
        from ..utils.persian_utils import format_currency
        info_layout.addRow("مبلغ کل:", QLabel(format_currency(self.policy.total_amount)))
        info_layout.addRow("پیش‌پرداخت:", QLabel(format_currency(self.policy.down_payment)))
        remaining = self.policy.total_amount - self.policy.down_payment
        info_layout.addRow("باقی‌مانده:", QLabel(format_currency(remaining)))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Installments table
        table_label = QLabel("لیست اقساط")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره قسط", "مبلغ", "تاریخ سررسید", "تاریخ پرداخت", 
            "وضعیت", "روش پرداخت", "عملیات"
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
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_installments(self):
        """Load installments for this policy"""
        from ..controllers import InstallmentController
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        try:
            controller = InstallmentController(self.session)
            installments = controller.get_policy_installments(self.policy.id)
            
            self.table.setRowCount(len(installments))
            
            for row, inst in enumerate(installments):
                self.table.setItem(row, 0, QTableWidgetItem(str(inst.installment_number)))
                self.table.setItem(row, 1, QTableWidgetItem(format_currency(inst.amount)))
                self.table.setItem(row, 2, QTableWidgetItem(
                    PersianDateConverter.gregorian_to_jalali(inst.due_date)
                ))
                
                payment_date = "-"
                if inst.payment_date:
                    payment_date = PersianDateConverter.gregorian_to_jalali(inst.payment_date)
                self.table.setItem(row, 3, QTableWidgetItem(payment_date))
                
                # Status with color coding
                status_item = QTableWidgetItem(self.get_status_text(inst.status))
                status_item.setBackground(self.get_status_color(inst.status))
                self.table.setItem(row, 4, status_item)
                
                self.table.setItem(row, 5, QTableWidgetItem(inst.payment_method or "-"))
                
                # Action buttons
                if inst.status in ['pending', 'overdue']:
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    
                    pay_btn = QPushButton("ثبت پرداخت")
                    pay_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover { background-color: #229954; }
                    """)
                    pay_btn.clicked.connect(lambda checked, i=inst: self.mark_paid(i))
                    btn_layout.addWidget(pay_btn)
                    
                    btn_widget.setLayout(btn_layout)
                    self.table.setCellWidget(row, 6, btn_widget)
                else:
                    self.table.setItem(row, 6, QTableWidgetItem(""))
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error loading installments: {e}")
            QMessageBox.warning(self, "خطا", "خطا در بارگذاری اقساط")
    
    def get_status_text(self, status):
        """Get Persian text for status"""
        status_map = {
            'pending': 'در انتظار',
            'paid': 'پرداخت شده',
            'overdue': 'معوق',
            'cancelled': 'لغو شده'
        }
        return status_map.get(status, status)
    
    def get_status_color(self, status):
        """Get color for status"""
        from PyQt5.QtGui import QColor
        
        color_map = {
            'pending': QColor(243, 156, 18, 100),  # Orange
            'paid': QColor(39, 174, 96, 100),      # Green
            'overdue': QColor(231, 76, 60, 100),   # Red
            'cancelled': QColor(149, 165, 166, 100) # Gray
        }
        return color_map.get(status, QColor(255, 255, 255))
    
    def mark_paid(self, installment):
        """Mark installment as paid"""
        from ..controllers import InstallmentController
        
        reply = QMessageBox.question(
            self,
            'تأیید پرداخت',
            f'آیا پرداخت قسط شماره {installment.installment_number} را تأیید می‌کنید؟',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            controller = InstallmentController(self.session)
            success, message = controller.mark_as_paid(installment.id, payment_method='نقدی')
            
            if success:
                QMessageBox.information(self, "موفق", message)
                self.load_installments()
            else:
                QMessageBox.warning(self, "خطا", message)
