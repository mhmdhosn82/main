"""
Policy management widget for creating and editing insurance policies.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QDialog, QFormLayout, QLineEdit, QMessageBox,
                            QHeaderView, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from src.database.db import Database
from src.models.repository import PolicyRepository, InstallmentRepository
from src.models.models import InsurancePolicy
from src.utils.helpers import generate_installments, get_current_jalali_date
from src.utils.export import export_policies_to_excel, export_policies_to_pdf


class PolicyManagementWidget(QWidget):
    """Widget for managing insurance policies."""
    
    policy_selected = pyqtSignal(int)
    
    def __init__(self, db: Database):
        """
        Initialize the policy management widget.
        
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
        
        # Title and buttons
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)
        
        title = QLabel("مدیریت بیمه‌نامه‌ها")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Export buttons
        export_excel_btn = QPushButton("خروجی Excel")
        export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_excel_btn.clicked.connect(self.export_to_excel)
        header_layout.addWidget(export_excel_btn)
        
        export_pdf_btn = QPushButton("خروجی PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_to_pdf)
        header_layout.addWidget(export_pdf_btn)
        
        new_policy_btn = QPushButton("ثبت بیمه‌نامه جدید")
        new_policy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_policy_btn.clicked.connect(self.show_new_policy_dialog)
        header_layout.addWidget(new_policy_btn)
        
        # Search
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)
        
        search_label = QLabel("جستجو:")
        search_label.setStyleSheet("font-size: 11pt;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره بیمه‌نامه یا نام بیمه‌شده...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        self.search_input.textChanged.connect(self.search_policies)
        search_layout.addWidget(self.search_input, stretch=1)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "نام بیمه‌شده", "تاریخ صدور", "تاریخ انقضا",
            "پیش‌پرداخت", "مجموع اقساط", "تعداد اقساط", "عملیات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
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
        layout.addWidget(self.table)
        
    def refresh_data(self):
        """Refresh the policies table."""
        self.load_policies()
        
    def load_policies(self, search_term: str = ""):
        """
        Load policies into the table.
        
        Args:
            search_term: Optional search term
        """
        policies = self.policy_repo.get_all_policies(search_term)
        
        self.table.setRowCount(0)
        for i, policy in enumerate(policies):
            self.table.insertRow(i)
            
            self.table.setItem(i, 0, QTableWidgetItem(policy.policy_number))
            self.table.setItem(i, 1, QTableWidgetItem(policy.insured_name))
            self.table.setItem(i, 2, QTableWidgetItem(policy.issuance_date))
            self.table.setItem(i, 3, QTableWidgetItem(policy.expiration_date))
            self.table.setItem(i, 4, QTableWidgetItem(f"{policy.advance_payment:,.0f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{policy.total_installment_amount:,.0f}"))
            self.table.setItem(i, 6, QTableWidgetItem(str(policy.number_of_installments)))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_widget.setLayout(actions_layout)
            
            view_btn = QPushButton("مشاهده اقساط")
            view_btn.setStyleSheet("background-color: #3498db; color: white; padding: 5px; border-radius: 3px;")
            view_btn.clicked.connect(lambda checked, pid=policy.id: self.policy_selected.emit(pid))
            actions_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("ویرایش")
            edit_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 5px; border-radius: 3px;")
            edit_btn.clicked.connect(lambda checked, p=policy: self.show_edit_policy_dialog(p))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("حذف")
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, pid=policy.id: self.delete_policy(pid))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(i, 7, actions_widget)
    
    def search_policies(self):
        """Search policies based on input."""
        search_term = self.search_input.text()
        self.load_policies(search_term)
    
    def show_new_policy_dialog(self):
        """Show dialog for creating a new policy."""
        dialog = PolicyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            policy_data = dialog.get_policy_data()
            self.create_policy(policy_data)
    
    def show_edit_policy_dialog(self, policy: InsurancePolicy):
        """
        Show dialog for editing a policy.
        
        Args:
            policy: The policy to edit
        """
        dialog = PolicyDialog(self, policy)
        if dialog.exec_() == QDialog.Accepted:
            policy_data = dialog.get_policy_data()
            policy_data['id'] = policy.id
            self.update_policy(policy_data)
    
    def create_policy(self, policy_data: dict):
        """
        Create a new policy.
        
        Args:
            policy_data: Dictionary with policy data
        """
        try:
            policy = InsurancePolicy(**policy_data)
            policy_id = self.policy_repo.create_policy(policy)
            
            # Generate installments
            installments = generate_installments(
                policy_id,
                policy.issuance_date,
                policy.number_of_installments,
                policy.total_installment_amount
            )
            
            for installment in installments:
                self.installment_repo.create_installment(installment)
            
            QMessageBox.information(self, "موفق", "بیمه‌نامه با موفقیت ثبت شد.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت بیمه‌نامه: {str(e)}")
    
    def update_policy(self, policy_data: dict):
        """
        Update an existing policy.
        
        Args:
            policy_data: Dictionary with policy data
        """
        try:
            policy = InsurancePolicy(**policy_data)
            self.policy_repo.update_policy(policy)
            
            QMessageBox.information(self, "موفق", "بیمه‌نامه با موفقیت به‌روزرسانی شد.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی بیمه‌نامه: {str(e)}")
    
    def delete_policy(self, policy_id: int):
        """
        Delete a policy.
        
        Args:
            policy_id: The policy ID
        """
        reply = QMessageBox.question(
            self, 
            "تایید حذف",
            "آیا از حذف این بیمه‌نامه و تمام اقساط آن اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.policy_repo.delete_policy(policy_id)
                QMessageBox.information(self, "موفق", "بیمه‌نامه با موفقیت حذف شد.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف بیمه‌نامه: {str(e)}")
    
    def export_to_excel(self):
        """Export policies to Excel."""
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if filename:
            try:
                policies = self.policy_repo.get_all_policies()
                policies_data = [p.to_dict() for p in policies]
                export_policies_to_excel(policies_data, filename)
                QMessageBox.information(self, "موفق", "خروجی Excel با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def export_to_pdf(self):
        """Export policies to PDF."""
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")
        if filename:
            try:
                policies = self.policy_repo.get_all_policies()
                policies_data = [p.to_dict() for p in policies]
                export_policies_to_pdf(policies_data, filename)
                QMessageBox.information(self, "موفق", "خروجی PDF با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")


class PolicyDialog(QDialog):
    """Dialog for creating/editing a policy."""
    
    def __init__(self, parent=None, policy: InsurancePolicy = None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            policy: Existing policy for editing (optional)
        """
        super().__init__(parent)
        self.policy = policy
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ثبت بیمه‌نامه جدید" if not self.policy else "ویرایش بیمه‌نامه")
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Form fields
        self.policy_number_input = QLineEdit()
        self.insured_name_input = QLineEdit()
        self.issuance_date_input = QLineEdit()
        self.issuance_date_input.setPlaceholderText("مثال: 1402/01/01")
        self.expiration_date_input = QLineEdit()
        self.expiration_date_input.setPlaceholderText("مثال: 1403/01/01")
        self.advance_payment_input = QLineEdit()
        self.total_installment_input = QLineEdit()
        self.num_installments_input = QLineEdit()
        
        # Set initial values if editing
        if self.policy:
            self.policy_number_input.setText(self.policy.policy_number)
            self.insured_name_input.setText(self.policy.insured_name)
            self.issuance_date_input.setText(self.policy.issuance_date)
            self.expiration_date_input.setText(self.policy.expiration_date)
            self.advance_payment_input.setText(str(self.policy.advance_payment))
            self.total_installment_input.setText(str(self.policy.total_installment_amount))
            self.num_installments_input.setText(str(self.policy.number_of_installments))
        else:
            # Set default issuance date
            self.issuance_date_input.setText(get_current_jalali_date())
        
        layout.addRow("شماره بیمه‌نامه:", self.policy_number_input)
        layout.addRow("نام بیمه‌شده:", self.insured_name_input)
        layout.addRow("تاریخ صدور:", self.issuance_date_input)
        layout.addRow("تاریخ انقضا:", self.expiration_date_input)
        layout.addRow("مبلغ پیش‌پرداخت:", self.advance_payment_input)
        layout.addRow("مجموع مبلغ اقساط:", self.total_installment_input)
        layout.addRow("تعداد اقساط:", self.num_installments_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        layout.addRow(buttons_layout)
        
        save_btn = QPushButton("ذخیره")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
    
    def get_policy_data(self) -> dict:
        """
        Get policy data from form.
        
        Returns:
            Dictionary with policy data
        """
        return {
            'policy_number': self.policy_number_input.text(),
            'insured_name': self.insured_name_input.text(),
            'issuance_date': self.issuance_date_input.text(),
            'expiration_date': self.expiration_date_input.text(),
            'advance_payment': float(self.advance_payment_input.text()),
            'total_installment_amount': float(self.total_installment_input.text()),
            'number_of_installments': int(self.num_installments_input.text()),
        }
