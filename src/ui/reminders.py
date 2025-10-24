"""
Reminders widget for viewing due installments.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QLineEdit, QDateEdit, QMessageBox,
                            QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from src.database.db import Database
from src.models.repository import InstallmentRepository
from src.utils.helpers import (get_current_jalali_date, compare_dates, 
                              jalali_to_gregorian, gregorian_to_jalali)
from src.utils.export import export_installments_to_excel, export_installments_to_pdf


class RemindersWidget(QWidget):
    """Widget for viewing installment reminders."""
    
    def __init__(self, db: Database):
        """
        Initialize the reminders widget.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.installment_repo = InstallmentRepository(db)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title and buttons
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)
        
        title = QLabel("یادآوری اقساط سررسید")
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
        
        # Date range filter
        filter_layout = QHBoxLayout()
        layout.addLayout(filter_layout)
        
        filter_label = QLabel("فیلتر بر اساس تاریخ:")
        filter_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        filter_layout.addWidget(filter_label)
        
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("از تاریخ (مثال: 1402/01/01)")
        self.start_date_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        filter_layout.addWidget(self.start_date_input)
        
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("تا تاریخ (مثال: 1403/01/01)")
        self.end_date_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        filter_layout.addWidget(self.end_date_input)
        
        apply_filter_btn = QPushButton("اعمال فیلتر")
        apply_filter_btn.setStyleSheet("""
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
        apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_filter_btn)
        
        clear_filter_btn = QPushButton("پاک کردن فیلتر")
        clear_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_filter_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(clear_filter_btn)
        
        filter_layout.addStretch()
        
        # Quick filter buttons
        quick_filter_layout = QHBoxLayout()
        layout.addLayout(quick_filter_layout)
        
        today_btn = QPushButton("امروز")
        today_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px 15px; border-radius: 5px;")
        today_btn.clicked.connect(self.show_today)
        quick_filter_layout.addWidget(today_btn)
        
        this_week_btn = QPushButton("این هفته")
        this_week_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px 15px; border-radius: 5px;")
        this_week_btn.clicked.connect(self.show_this_week)
        quick_filter_layout.addWidget(this_week_btn)
        
        this_month_btn = QPushButton("این ماه")
        this_month_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px 15px; border-radius: 5px;")
        this_month_btn.clicked.connect(self.show_this_month)
        quick_filter_layout.addWidget(this_month_btn)
        
        all_btn = QPushButton("همه")
        all_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px 15px; border-radius: 5px;")
        all_btn.clicked.connect(self.show_all)
        quick_filter_layout.addWidget(all_btn)
        
        quick_filter_layout.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "شماره بیمه‌نامه", "نام بیمه‌شده", "شماره قسط", "تاریخ سررسید", "مبلغ", "وضعیت"
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
        """Refresh the reminders data."""
        self.show_all()
    
    def load_installments(self, start_date: str = None, end_date: str = None):
        """
        Load installments within a date range.
        
        Args:
            start_date: Start date in Jalali format
            end_date: End date in Jalali format
        """
        installments = self.installment_repo.get_due_installments(start_date, end_date)
        
        self.table.setRowCount(0)
        for i, inst in enumerate(installments):
            self.table.insertRow(i)
            
            self.table.setItem(i, 0, QTableWidgetItem(inst['policy_number']))
            self.table.setItem(i, 1, QTableWidgetItem(inst['insured_name']))
            self.table.setItem(i, 2, QTableWidgetItem(str(inst['installment_number'])))
            
            # Highlight overdue dates
            due_date_item = QTableWidgetItem(inst['due_date'])
            current_date = get_current_jalali_date()
            if compare_dates(inst['due_date'], current_date) < 0:
                due_date_item.setBackground(QColor("#fadbd8"))
            elif compare_dates(inst['due_date'], current_date) == 0:
                due_date_item.setBackground(QColor("#fff3cd"))
            self.table.setItem(i, 3, due_date_item)
            
            self.table.setItem(i, 4, QTableWidgetItem(f"{inst['amount']:,.0f} ریال"))
            
            status_item = QTableWidgetItem("پرداخت شده" if inst['status'] == 'paid' else "پرداخت نشده")
            if inst['status'] == 'paid':
                status_item.setBackground(QColor("#d5f4e6"))
            else:
                status_item.setBackground(QColor("#fadbd8"))
            self.table.setItem(i, 5, status_item)
    
    def apply_filter(self):
        """Apply date range filter."""
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()
        
        if not start_date or not end_date:
            QMessageBox.warning(self, "هشدار", "لطفا هر دو تاریخ را وارد کنید.")
            return
        
        self.load_installments(start_date, end_date)
    
    def clear_filter(self):
        """Clear date filter."""
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.show_all()
    
    def show_today(self):
        """Show installments due today."""
        current_date = get_current_jalali_date()
        self.start_date_input.setText(current_date)
        self.end_date_input.setText(current_date)
        self.load_installments(current_date, current_date)
    
    def show_this_week(self):
        """Show installments due this week."""
        from datetime import timedelta
        current_date = get_current_jalali_date()
        
        # Get end of week (7 days from now)
        greg_date = jalali_to_gregorian(current_date)
        end_greg = greg_date + timedelta(days=7)
        end_date = gregorian_to_jalali(end_greg)
        
        self.start_date_input.setText(current_date)
        self.end_date_input.setText(end_date)
        self.load_installments(current_date, end_date)
    
    def show_this_month(self):
        """Show installments due this month."""
        from datetime import timedelta
        current_date = get_current_jalali_date()
        
        # Get end of month (30 days from now)
        greg_date = jalali_to_gregorian(current_date)
        end_greg = greg_date + timedelta(days=30)
        end_date = gregorian_to_jalali(end_greg)
        
        self.start_date_input.setText(current_date)
        self.end_date_input.setText(end_date)
        self.load_installments(current_date, end_date)
    
    def show_all(self):
        """Show all unpaid installments."""
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.load_installments()
    
    def export_to_excel(self):
        """Export reminders to Excel."""
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if filename:
            try:
                start_date = self.start_date_input.text() or None
                end_date = self.end_date_input.text() or None
                installments = self.installment_repo.get_due_installments(start_date, end_date)
                
                export_installments_to_excel(installments, filename)
                QMessageBox.information(self, "موفق", "خروجی Excel با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def export_to_pdf(self):
        """Export reminders to PDF."""
        filename, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")
        if filename:
            try:
                start_date = self.start_date_input.text() or None
                end_date = self.end_date_input.text() or None
                installments = self.installment_repo.get_due_installments(start_date, end_date)
                
                export_installments_to_pdf(installments, filename)
                QMessageBox.information(self, "موفق", "خروجی PDF با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
