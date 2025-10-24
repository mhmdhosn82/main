"""Policy management widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QMessageBox, QDialog, QFormLayout, QComboBox,
                            QDateEdit, QTextEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .persian_date_edit import PersianDateEdit
import logging

logger = logging.getLogger(__name__)

class PolicyWidget(QWidget):
    """Policy management interface"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.load_policies()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("مدیریت بیمه‌نامه‌ها")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add button
        add_btn = QPushButton("+ بیمه‌نامه جدید")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        add_btn.clicked.connect(self.show_add_policy_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو...")
        self.search_input.textChanged.connect(self.search_policies)
        search_layout.addWidget(QLabel("جستجو:"))
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "بیمه‌گذار", "نوع", "شرکت بیمه",
            "مبلغ کل", "وضعیت", "عملیات"
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
    
    def load_policies(self):
        """Load policies into table"""
        from ..controllers import PolicyController
        from ..utils.persian_utils import format_currency
        
        try:
            controller = PolicyController(self.session)
            policies = controller.get_all_policies(self.user.id)
            
            self.table.setRowCount(len(policies))
            
            for row, policy in enumerate(policies):
                self.table.setItem(row, 0, QTableWidgetItem(policy.policy_number))
                self.table.setItem(row, 1, QTableWidgetItem(policy.policy_holder_name))
                self.table.setItem(row, 2, QTableWidgetItem(policy.policy_type or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(policy.insurance_company or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(format_currency(policy.total_amount)))
                self.table.setItem(row, 5, QTableWidgetItem(policy.status))
                
                # Action buttons
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("مشاهده")
                view_btn.clicked.connect(lambda checked, p=policy: self.view_policy(p))
                btn_layout.addWidget(view_btn)
                
                installments_btn = QPushButton("مدیریت اقساط")
                installments_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover { background-color: #2980b9; }
                """)
                installments_btn.clicked.connect(lambda checked, p=policy: self.manage_installments(p))
                btn_layout.addWidget(installments_btn)
                
                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(row, 6, btn_widget)
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            QMessageBox.warning(self, "خطا", "خطا در بارگذاری بیمه‌نامه‌ها")
    
    def show_add_policy_dialog(self):
        """Show add policy dialog"""
        dialog = AddPolicyDialog(self.user, self.session, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_policies()
    
    def view_policy(self, policy):
        """View policy details"""
        QMessageBox.information(
            self,
            "جزئیات بیمه‌نامه",
            f"شماره: {policy.policy_number}\n"
            f"بیمه‌گذار: {policy.policy_holder_name}\n"
            f"موبایل: {policy.mobile_number or '-'}\n"
            f"نوع: {policy.policy_type}\n"
            f"شرکت: {policy.insurance_company or '-'}\n"
            f"وضعیت: {policy.status}"
        )
    
    def manage_installments(self, policy):
        """Open installment management page for policy"""
        from .policy_installment_management import PolicyInstallmentDialog
        dialog = PolicyInstallmentDialog(policy, self.session, self)
        dialog.exec_()
    
    def search_policies(self, text):
        """Search policies"""
        for row in range(self.table.rowCount()):
            show = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(row, not show)
    
    def refresh(self):
        """Refresh table"""
        self.load_policies()


class AddPolicyDialog(QDialog):
    """Dialog for adding new policy"""
    
    def __init__(self, user, session, parent=None):
        super().__init__(parent)
        self.user = user
        self.session = session
        self.setWindowTitle("بیمه‌نامه جدید")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QFormLayout()
        
        self.policy_number = QLineEdit()
        self.holder_name = QLineEdit()
        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText("مثال: 09123456789")
        
        self.policy_type = QComboBox()
        self.policy_type.addItems(["شخص ثالث", "بدنه", "عمر", "حوادث", "آتش‌سوزی"])
        
        self.total_amount = QDoubleSpinBox()
        self.total_amount.setMaximum(999999999999)
        self.total_amount.setGroupSeparatorShown(True)
        self.total_amount.setSuffix(" ریال")
        
        self.down_payment = QDoubleSpinBox()
        self.down_payment.setMaximum(999999999999)
        self.down_payment.setGroupSeparatorShown(True)
        self.down_payment.setSuffix(" ریال")
        
        self.num_installments = QComboBox()
        self.num_installments.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "18", "24", "36"])
        self.num_installments.setCurrentText("12")
        
        self.start_date = PersianDateEdit()
        self.start_date.setDate(QDate.currentDate())
        
        self.end_date = PersianDateEdit()
        self.end_date.setDate(QDate.currentDate().addYears(1))
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        
        layout.addRow("شماره بیمه‌نامه:", self.policy_number)
        layout.addRow("نام بیمه‌گذار:", self.holder_name)
        layout.addRow("شماره موبایل:", self.mobile_number)
        layout.addRow("نوع بیمه:", self.policy_type)
        layout.addRow("مبلغ کل بیمه:", self.total_amount)
        layout.addRow("مبلغ پیش‌پرداخت:", self.down_payment)
        layout.addRow("تعداد اقساط:", self.num_installments)
        layout.addRow("تاریخ صدور (شمسی):", self.start_date)
        layout.addRow("تاریخ پایان (شمسی):", self.end_date)
        layout.addRow("توضیحات:", self.description)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save_policy)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def save_policy(self):
        """Save policy"""
        from ..controllers import PolicyController, InstallmentController
        from dateutil.relativedelta import relativedelta
        
        if not self.policy_number.text() or not self.holder_name.text():
            QMessageBox.warning(self, "خطا", "لطفاً فیلدهای ضروری را پر کنید")
            return
        
        # Validate mobile number
        mobile = self.mobile_number.text().strip()
        if mobile and (not mobile.startswith('09') or len(mobile) != 11):
            QMessageBox.warning(self, "خطا", "شماره موبایل باید با 09 شروع شده و 11 رقم باشد")
            return
        
        total_amount = self.total_amount.value()
        down_payment = self.down_payment.value()
        num_installments = int(self.num_installments.currentText())
        
        # Validate total amount
        if total_amount <= 0:
            QMessageBox.warning(self, "خطا", "مبلغ کل بیمه باید بیشتر از صفر باشد")
            return
        
        # Validate down payment
        if down_payment > total_amount:
            QMessageBox.warning(self, "خطا", "مبلغ پیش‌پرداخت نمی‌تواند بیشتر از مبلغ کل باشد")
            return
        
        # Validate dates
        if self.end_date.date() <= self.start_date.date():
            QMessageBox.warning(self, "خطا", "تاریخ پایان باید بعد از تاریخ شروع باشد")
            return
        
        policy_data = {
            'policy_number': self.policy_number.text(),
            'policy_holder_name': self.holder_name.text(),
            'mobile_number': mobile,
            'policy_type': self.policy_type.currentText(),
            'total_amount': total_amount,
            'down_payment': down_payment,
            'num_installments': num_installments,
            'start_date': self.start_date.date().toPyDate(),
            'end_date': self.end_date.date().toPyDate(),
            'description': self.description.toPlainText()
        }
        
        controller = PolicyController(self.session)
        success, message, policy = controller.create_policy(self.user.id, policy_data)
        
        if success and policy:
            # Create installments: remaining amount after down payment divided by num_installments
            remaining_amount = total_amount - down_payment
            if remaining_amount > 0 and num_installments > 0:
                installment_ctrl = InstallmentController(self.session)
                # First installment starts next month
                start_date = self.start_date.date().toPyDate()
                first_installment_date = start_date + relativedelta(months=1)
                
                success_inst, msg_inst, _ = installment_ctrl.create_installments_batch(
                    policy.id,
                    remaining_amount,
                    num_installments,
                    first_installment_date,
                    interval_days=30
                )
                
                if success_inst:
                    QMessageBox.information(self, "موفق", 
                        f"{message}\n{msg_inst}")
                else:
                    QMessageBox.warning(self, "هشدار", 
                        f"{message}\nاما خطا در ایجاد اقساط: {msg_inst}")
            else:
                QMessageBox.information(self, "موفق", message)
            
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", message)
