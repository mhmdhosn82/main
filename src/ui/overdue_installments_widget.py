"""Overdue installments management widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import logging

from ..models import Installment, InsurancePolicy
from ..utils.persian_utils import format_currency, PersianDateConverter
from ..controllers import InstallmentController

logger = logging.getLogger(__name__)

# Constant for overdue threshold
OVERDUE_THRESHOLD_DAYS = 30

class OverdueInstallmentsWidget(QWidget):
    """Widget for managing overdue installments (>1 month past due)"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.load_overdue_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("اقساط معوق")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        refresh_btn.clicked.connect(self.load_overdue_installments)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("اقساطی که بیش از یک ماه از تاریخ سررسید آنها گذشته و هنوز پرداخت نشده‌اند")
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Scroll area for policy groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.policies_widget = QWidget()
        self.policies_layout = QVBoxLayout()
        self.policies_widget.setLayout(self.policies_layout)
        scroll.setWidget(self.policies_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def load_overdue_installments(self):
        """Load overdue installments grouped by policy"""
        
        # Clear existing widgets
        while self.policies_layout.count():
            child = self.policies_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        try:
            # Get overdue installments - more than OVERDUE_THRESHOLD_DAYS days past due and not paid
            today = datetime.now()
            threshold_date = today - timedelta(days=OVERDUE_THRESHOLD_DAYS)
            
            query = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(
                InsurancePolicy.user_id == self.user.id,
                Installment.due_date < threshold_date,
                Installment.status.in_(['pending', 'overdue'])
            ).order_by(InsurancePolicy.policy_number, Installment.installment_number)
            
            installments = query.all()
            
            if not installments:
                no_data = QLabel("هیچ قسط معوقی یافت نشد! ✓")
                no_data.setStyleSheet("""
                    QLabel {
                        font-size: 16pt;
                        color: #27ae60;
                        padding: 50px;
                        background: white;
                        border: 2px dashed #27ae60;
                        border-radius: 10px;
                    }
                """)
                no_data.setAlignment(Qt.AlignCenter)
                self.policies_layout.addWidget(no_data)
                return
            
            # Group by policy
            policies_dict = {}
            for inst, policy in installments:
                if policy.id not in policies_dict:
                    policies_dict[policy.id] = {
                        'policy': policy,
                        'installments': []
                    }
                policies_dict[policy.id]['installments'].append(inst)
            
            # Create a group box for each policy
            for policy_id, policy_data in policies_dict.items():
                policy = policy_data['policy']
                installments_list = policy_data['installments']
                
                group = QGroupBox()
                group.setStyleSheet("""
                    QGroupBox {
                        background: white;
                        border: 2px solid #e74c3c;
                        border-radius: 8px;
                        margin-top: 15px;
                        padding: 15px;
                        font-weight: bold;
                    }
                """)
                
                group_layout = QVBoxLayout()
                
                # Policy header
                policy_header = QLabel(
                    f"📋 بیمه‌نامه: {policy.policy_number} | "
                    f"بیمه‌گذار: {policy.policy_holder_name} | "
                    f"نوع: {policy.policy_type or '-'} | "
                    f"تعداد اقساط معوق: {len(installments_list)}"
                )
                policy_header.setStyleSheet("""
                    QLabel {
                        font-size: 12pt;
                        font-weight: bold;
                        color: #2c3e50;
                        background: #ecf0f1;
                        padding: 10px;
                        border-radius: 5px;
                    }
                """)
                group_layout.addWidget(policy_header)
                
                # Table for installments
                table = QTableWidget()
                table.setColumnCount(6)
                table.setHorizontalHeaderLabels([
                    "شماره قسط", "مبلغ", "تاریخ سررسید", "تعداد روزهای تأخیر", "وضعیت", "عملیات"
                ])
                table.setLayoutDirection(Qt.RightToLeft)
                table.setRowCount(len(installments_list))
                table.setStyleSheet("""
                    QTableWidget {
                        background-color: white;
                        border: 1px solid #bdc3c7;
                        gridline-color: #ecf0f1;
                    }
                    QHeaderView::section {
                        background-color: #e74c3c;
                        color: white;
                        padding: 8px;
                        font-weight: bold;
                    }
                """)
                
                for row, inst in enumerate(installments_list):
                    # Installment number
                    table.setItem(row, 0, QTableWidgetItem(str(inst.installment_number)))
                    
                    # Amount
                    table.setItem(row, 1, QTableWidgetItem(format_currency(inst.amount)))
                    
                    # Due date
                    table.setItem(row, 2, QTableWidgetItem(
                        PersianDateConverter.gregorian_to_jalali(inst.due_date)
                    ))
                    
                    # Days overdue
                    days_overdue = (today - inst.due_date).days
                    overdue_item = QTableWidgetItem(f"{days_overdue} روز")
                    overdue_item.setForeground(Qt.red)
                    table.setItem(row, 3, overdue_item)
                    
                    # Status
                    status_text = "معوق" if inst.status == 'overdue' else "در انتظار"
                    status_item = QTableWidgetItem(status_text)
                    status_item.setForeground(Qt.red)
                    table.setItem(row, 4, status_item)
                    
                    # Action buttons
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(5, 5, 5, 5)
                    
                    view_btn = QPushButton("مشاهده")
                    view_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                        }
                        QPushButton:hover { background-color: #2980b9; }
                    """)
                    view_btn.clicked.connect(lambda checked, i=inst, p=policy: self.view_details(i, p))
                    btn_layout.addWidget(view_btn)
                    
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
                    table.setCellWidget(row, 5, btn_widget)
                
                table.resizeColumnsToContents()
                group_layout.addWidget(table)
                
                group.setLayout(group_layout)
                self.policies_layout.addWidget(group)
            
            self.policies_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error loading overdue installments: {e}")
            QMessageBox.warning(self, "خطا", "خطا در بارگذاری اقساط معوق")
    
    def view_details(self, installment, policy):
        """View installment and policy details"""
        
        details = (
            f"جزئیات قسط معوق:\n\n"
            f"بیمه‌نامه: {policy.policy_number}\n"
            f"بیمه‌گذار: {policy.policy_holder_name}\n"
            f"موبایل: {policy.mobile_number or '-'}\n"
            f"نوع بیمه: {policy.policy_type or '-'}\n\n"
            f"شماره قسط: {installment.installment_number}\n"
            f"مبلغ: {format_currency(installment.amount)}\n"
            f"تاریخ سررسید: {PersianDateConverter.gregorian_to_jalali(installment.due_date)}\n"
            f"روزهای تأخیر: {(datetime.now() - installment.due_date).days} روز\n"
            f"وضعیت: {installment.status}"
        )
        
        QMessageBox.information(self, "جزئیات قسط معوق", details)
    
    def mark_paid(self, installment):
        """Mark installment as paid"""
        
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
                self.load_overdue_installments()
            else:
                QMessageBox.warning(self, "خطا", message)
    
    def refresh(self):
        """Refresh the widget"""
        self.load_overdue_installments()
