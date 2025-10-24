"""Policy management widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QMessageBox, QDialog, QFormLayout, QComboBox,
                            QDateEdit, QTextEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
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
            f"نوع: {policy.policy_type}\n"
            f"شرکت: {policy.insurance_company}\n"
            f"وضعیت: {policy.status}"
        )
    
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
        self.holder_national_id = QLineEdit()
        
        self.policy_type = QComboBox()
        self.policy_type.addItems(["عمر", "درمان", "اتومبیل", "آتش‌سوزی", "سایر"])
        
        self.insurance_company = QLineEdit()
        
        self.total_amount = QDoubleSpinBox()
        self.total_amount.setMaximum(999999999)
        self.total_amount.setSuffix(" ریال")
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        
        layout.addRow("شماره بیمه‌نامه:", self.policy_number)
        layout.addRow("نام بیمه‌گذار:", self.holder_name)
        layout.addRow("کد ملی:", self.holder_national_id)
        layout.addRow("نوع بیمه:", self.policy_type)
        layout.addRow("شرکت بیمه:", self.insurance_company)
        layout.addRow("مبلغ کل:", self.total_amount)
        layout.addRow("تاریخ شروع:", self.start_date)
        layout.addRow("تاریخ پایان:", self.end_date)
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
        from ..controllers import PolicyController
        
        if not self.policy_number.text() or not self.holder_name.text():
            QMessageBox.warning(self, "خطا", "لطفاً فیلدهای ضروری را پر کنید")
            return
        
        policy_data = {
            'policy_number': self.policy_number.text(),
            'policy_holder_name': self.holder_name.text(),
            'policy_holder_national_id': self.holder_national_id.text(),
            'policy_type': self.policy_type.currentText(),
            'insurance_company': self.insurance_company.text(),
            'total_amount': self.total_amount.value(),
            'start_date': self.start_date.date().toPyDate(),
            'end_date': self.end_date.date().toPyDate(),
            'description': self.description.toPlainText()
        }
        
        controller = PolicyController(self.session)
        success, message, policy = controller.create_policy(self.user.id, policy_data)
        
        if success:
            QMessageBox.information(self, "موفق", message)
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", message)
