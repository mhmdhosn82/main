"""
Installment management widget for viewing and managing installments.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.database.db import Database
from src.models.repository import PolicyRepository, InstallmentRepository
from src.utils.helpers import get_current_jalali_date
from src.utils.export import export_installments_to_excel, export_installments_to_pdf


class InstallmentManagementWidget(QWidget):
    """Widget for managing installments."""
    
    def __init__(self, db: Database):
        """
        Initialize the installment management widget.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.installment_repo = InstallmentRepository(db)
        self.current_policy_id = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title and buttons
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)
        
        title = QLabel("مدیریت اقساط")
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
        
        # Policy selector
        selector_layout = QHBoxLayout()
        layout.addLayout(selector_layout)
        
        policy_label = QLabel("انتخاب بیمه‌نامه:")
        policy_label.setStyleSheet("font-size: 11pt;")
        selector_layout.addWidget(policy_label)
        
        self.policy_combo = QComboBox()
        self.policy_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        self.policy_combo.currentIndexChanged.connect(self.on_policy_selected)
        selector_layout.addWidget(self.policy_combo, stretch=1)
        
        # Policy info
        self.policy_info_label = QLabel("")
        self.policy_info_label.setStyleSheet("""
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-size: 11pt;
            margin: 10px 0;
        """)
        self.policy_info_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.policy_info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره قسط", "تاریخ سررسید", "مبلغ", "وضعیت", "تاریخ پرداخت", "عملیات", ""
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
        """Refresh the installments data."""
        self.load_policies()
        if self.current_policy_id:
            self.load_policy_installments(self.current_policy_id)
    
    def load_policies(self):
        """Load policies into combo box."""
        policies = self.policy_repo.get_all_policies()
        
        self.policy_combo.clear()
        self.policy_combo.addItem("-- انتخاب کنید --", None)
        
        for policy in policies:
            display_text = f"{policy.policy_number} - {policy.insured_name}"
            self.policy_combo.addItem(display_text, policy.id)
    
    def on_policy_selected(self, index):
        """Handle policy selection."""
        if index > 0:
            policy_id = self.policy_combo.currentData()
            self.load_policy_installments(policy_id)
    
    def load_policy_installments(self, policy_id: int):
        """
        Load installments for a specific policy.
        
        Args:
            policy_id: The policy ID
        """
        self.current_policy_id = policy_id
        
        # Get policy details
        policy = self.policy_repo.get_policy_by_id(policy_id)
        if not policy:
            return
        
        # Update policy info
        info_text = f"""
        <b>شماره بیمه‌نامه:</b> {policy.policy_number} | 
        <b>نام بیمه‌شده:</b> {policy.insured_name} | 
        <b>تاریخ صدور:</b> {policy.issuance_date} | 
        <b>پیش‌پرداخت:</b> {policy.advance_payment:,.0f} ریال | 
        <b>مجموع اقساط:</b> {policy.total_installment_amount:,.0f} ریال
        """
        self.policy_info_label.setText(info_text)
        
        # Set policy in combo
        for i in range(self.policy_combo.count()):
            if self.policy_combo.itemData(i) == policy_id:
                self.policy_combo.setCurrentIndex(i)
                break
        
        # Load installments
        installments = self.installment_repo.get_installments_by_policy(policy_id)
        
        self.table.setRowCount(0)
        for i, inst in enumerate(installments):
            self.table.insertRow(i)
            
            self.table.setItem(i, 0, QTableWidgetItem(str(inst.installment_number)))
            self.table.setItem(i, 1, QTableWidgetItem(inst.due_date))
            self.table.setItem(i, 2, QTableWidgetItem(f"{inst.amount:,.0f} ریال"))
            
            # Status with color
            status_item = QTableWidgetItem("پرداخت شده" if inst.status == 'paid' else "پرداخت نشده")
            if inst.status == 'paid':
                status_item.setBackground(QColor("#d5f4e6"))
            else:
                status_item.setBackground(QColor("#fadbd8"))
            self.table.setItem(i, 3, status_item)
            
            self.table.setItem(i, 4, QTableWidgetItem(inst.paid_date or "-"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_widget.setLayout(actions_layout)
            
            if inst.status == 'unpaid':
                mark_paid_btn = QPushButton("پرداخت شد")
                mark_paid_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 5px; border-radius: 3px;")
                mark_paid_btn.clicked.connect(lambda checked, iid=inst.id: self.mark_as_paid(iid))
                actions_layout.addWidget(mark_paid_btn)
            else:
                mark_unpaid_btn = QPushButton("پرداخت نشده")
                mark_unpaid_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 5px; border-radius: 3px;")
                mark_unpaid_btn.clicked.connect(lambda checked, iid=inst.id: self.mark_as_unpaid(iid))
                actions_layout.addWidget(mark_unpaid_btn)
            
            self.table.setCellWidget(i, 5, actions_widget)
    
    def mark_as_paid(self, installment_id: int):
        """
        Mark an installment as paid.
        
        Args:
            installment_id: The installment ID
        """
        try:
            current_date = get_current_jalali_date()
            self.installment_repo.update_installment_status(installment_id, 'paid', current_date)
            QMessageBox.information(self, "موفق", "قسط به عنوان پرداخت شده علامت‌گذاری شد.")
            self.load_policy_installments(self.current_policy_id)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی وضعیت: {str(e)}")
    
    def mark_as_unpaid(self, installment_id: int):
        """
        Mark an installment as unpaid.
        
        Args:
            installment_id: The installment ID
        """
        try:
            self.installment_repo.update_installment_status(installment_id, 'unpaid', None)
            QMessageBox.information(self, "موفق", "قسط به عنوان پرداخت نشده علامت‌گذاری شد.")
            self.load_policy_installments(self.current_policy_id)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی وضعیت: {str(e)}")
    
    def export_to_excel(self):
        """Export installments to Excel."""
        if not self.current_policy_id:
            QMessageBox.warning(self, "هشدار", "لطفا ابتدا یک بیمه‌نامه انتخاب کنید.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if filename:
            try:
                installments = self.installment_repo.get_installments_by_policy(self.current_policy_id)
                policy = self.policy_repo.get_policy_by_id(self.current_policy_id)
                
                installments_data = []
                for inst in installments:
                    data = inst.to_dict()
                    data['policy_number'] = policy.policy_number
                    data['insured_name'] = policy.insured_name
                    installments_data.append(data)
                
                export_installments_to_excel(installments_data, filename)
                QMessageBox.information(self, "موفق", "خروجی Excel با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def export_to_pdf(self):
        """Export installments to PDF."""
        if not self.current_policy_id:
            QMessageBox.warning(self, "هشدار", "لطفا ابتدا یک بیمه‌نامه انتخاب کنید.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")
        if filename:
            try:
                installments = self.installment_repo.get_installments_by_policy(self.current_policy_id)
                policy = self.policy_repo.get_policy_by_id(self.current_policy_id)
                
                installments_data = []
                for inst in installments:
                    data = inst.to_dict()
                    data['policy_number'] = policy.policy_number
                    data['insured_name'] = policy.insured_name
                    installments_data.append(data)
                
                export_installments_to_pdf(installments_data, filename)
                QMessageBox.information(self, "موفق", "خروجی PDF با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
