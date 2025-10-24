"""
Archive widget for viewing all policies with filters.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QLineEdit, QComboBox, QFileDialog,
                            QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.database.db import Database
from src.models.repository import PolicyRepository
from src.utils.helpers import get_current_jalali_date, compare_dates
from src.utils.export import export_policies_to_excel, export_policies_to_pdf


class ArchiveWidget(QWidget):
    """Widget for viewing archived and active policies."""
    
    policy_selected = pyqtSignal(int)
    
    def __init__(self, db: Database):
        """
        Initialize the archive widget.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title and buttons
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)
        
        title = QLabel("آرشیو بیمه‌نامه‌ها")
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
        
        # Filter controls
        filter_layout = QHBoxLayout()
        layout.addLayout(filter_layout)
        
        # Search
        search_label = QLabel("جستجو:")
        search_label.setStyleSheet("font-size: 11pt;")
        filter_layout.addWidget(search_label)
        
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
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, stretch=1)
        
        # Status filter
        status_label = QLabel("وضعیت:")
        status_label.setStyleSheet("font-size: 11pt;")
        filter_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "فعال", "منقضی"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "نام بیمه‌شده", "تاریخ صدور", "تاریخ انقضا",
            "پیش‌پرداخت", "مجموع اقساط", "تعداد اقساط", "وضعیت"
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
        """Refresh the archive data."""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and status filters."""
        search_term = self.search_input.text()
        status_filter = self.status_filter.currentText()
        
        # Get all policies
        policies = self.policy_repo.get_all_policies(search_term)
        
        # Filter by status
        current_date = get_current_jalali_date()
        filtered_policies = []
        
        for policy in policies:
            is_active = compare_dates(policy.expiration_date, current_date) >= 0
            
            if status_filter == "همه":
                filtered_policies.append(policy)
            elif status_filter == "فعال" and is_active:
                filtered_policies.append(policy)
            elif status_filter == "منقضی" and not is_active:
                filtered_policies.append(policy)
        
        # Display in table
        self.table.setRowCount(0)
        for i, policy in enumerate(filtered_policies):
            self.table.insertRow(i)
            
            self.table.setItem(i, 0, QTableWidgetItem(policy.policy_number))
            self.table.setItem(i, 1, QTableWidgetItem(policy.insured_name))
            self.table.setItem(i, 2, QTableWidgetItem(policy.issuance_date))
            self.table.setItem(i, 3, QTableWidgetItem(policy.expiration_date))
            self.table.setItem(i, 4, QTableWidgetItem(f"{policy.advance_payment:,.0f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{policy.total_installment_amount:,.0f}"))
            self.table.setItem(i, 6, QTableWidgetItem(str(policy.number_of_installments)))
            
            # Status
            is_active = compare_dates(policy.expiration_date, current_date) >= 0
            status_text = "فعال" if is_active else "منقضی"
            status_item = QTableWidgetItem(status_text)
            if is_active:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.red)
            self.table.setItem(i, 7, status_item)
    
    def export_to_excel(self):
        """Export policies to Excel."""
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if filename:
            try:
                search_term = self.search_input.text()
                policies = self.policy_repo.get_all_policies(search_term)
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
                search_term = self.search_input.text()
                policies = self.policy_repo.get_all_policies(search_term)
                policies_data = [p.to_dict() for p in policies]
                export_policies_to_pdf(policies_data, filename)
                QMessageBox.information(self, "موفق", "خروجی PDF با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
