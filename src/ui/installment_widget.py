"""Installment management widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QComboBox, QLineEdit, QDateEdit, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InstallmentWidget(QWidget):
    """Installment management interface"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.current_filter = "all"  # Default filter
        self.setup_ui()
        self.load_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title
        header_layout = QHBoxLayout()
        title = QLabel("مدیریت اقساط")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("نمایش و مدیریت تمام اقساط")
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Filters section
        filters_group = QGroupBox("فیلترها و جستجو")
        filters_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        filters_layout = QGridLayout()
        
        # Date filter
        date_filter_label = QLabel("فیلتر تاریخ:")
        self.date_filter = QComboBox()
        self.date_filter.addItems([
            "همه اقساط",
            "امروز",
            "7 روز آینده",
            "ماه آینده",
            "بازه تاریخی سفارشی"
        ])
        self.date_filter.currentTextChanged.connect(self.on_date_filter_changed)
        filters_layout.addWidget(date_filter_label, 0, 0)
        filters_layout.addWidget(self.date_filter, 0, 1)
        
        # Custom date range (initially hidden)
        self.start_date_label = QLabel("از تاریخ:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy/MM/dd")
        self.start_date.dateChanged.connect(self.apply_filters)
        self.start_date_label.hide()
        self.start_date.hide()
        filters_layout.addWidget(self.start_date_label, 0, 2)
        filters_layout.addWidget(self.start_date, 0, 3)
        
        self.end_date_label = QLabel("تا تاریخ:")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        self.end_date.setDisplayFormat("yyyy/MM/dd")
        self.end_date.dateChanged.connect(self.apply_filters)
        self.end_date_label.hide()
        self.end_date.hide()
        filters_layout.addWidget(self.end_date_label, 0, 4)
        filters_layout.addWidget(self.end_date, 0, 5)
        
        # Status filter
        status_filter_label = QLabel("وضعیت:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "در انتظار", "پرداخت شده", "معوق", "لغو شده"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(status_filter_label, 1, 0)
        filters_layout.addWidget(self.status_filter, 1, 1)
        
        # Search box
        search_label = QLabel("جستجو:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("جستجو بر اساس شماره بیمه‌نامه، نام بیمه‌گذار، یا شماره موبایل...")
        self.search_box.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(search_label, 1, 2)
        filters_layout.addWidget(self.search_box, 1, 3, 1, 3)
        
        # Reset filters button
        self.reset_btn = QPushButton("پاک کردن فیلترها")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.reset_btn.clicked.connect(self.reset_filters)
        filters_layout.addWidget(self.reset_btn, 2, 0, 1, 2)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Table with all installment fields
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
    
    def on_date_filter_changed(self, text):
        """Handle date filter change"""
        if text == "بازه تاریخی سفارشی":
            self.start_date_label.show()
            self.start_date.show()
            self.end_date_label.show()
            self.end_date.show()
        else:
            self.start_date_label.hide()
            self.start_date.hide()
            self.end_date_label.hide()
            self.end_date.hide()
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters and reload installments"""
        self.load_installments()
    
    def reset_filters(self):
        """Reset all filters to default"""
        self.date_filter.setCurrentText("همه اقساط")
        self.status_filter.setCurrentText("همه")
        self.search_box.clear()
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate().addMonths(1))
    
    def load_installments(self):
        """Load installments with filters applied"""
        from ..controllers import InstallmentController
        from ..models import InsurancePolicy
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        try:
            controller = InstallmentController(self.session)
            
            # Get all installments for the user
            from ..models import Installment
            
            # Start with base query
            query = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(
                InsurancePolicy.user_id == self.user.id
            )
            
            # Apply date filter
            date_filter_text = self.date_filter.currentText()
            today = datetime.now()
            
            if date_filter_text == "امروز":
                start_of_day = datetime(today.year, today.month, today.day)
                end_of_day = start_of_day + timedelta(days=1)
                query = query.filter(
                    Installment.due_date >= start_of_day,
                    Installment.due_date < end_of_day
                )
            elif date_filter_text == "7 روز آینده":
                future_date = today + timedelta(days=7)
                query = query.filter(
                    Installment.due_date >= today,
                    Installment.due_date <= future_date
                )
            elif date_filter_text == "ماه آینده":
                future_date = today + timedelta(days=30)
                query = query.filter(
                    Installment.due_date >= today,
                    Installment.due_date <= future_date
                )
            elif date_filter_text == "بازه تاریخی سفارشی":
                start_date = self.start_date.date().toPyDate()
                end_date = self.end_date.date().toPyDate()
                start_datetime = datetime(start_date.year, start_date.month, start_date.day)
                end_datetime = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
                query = query.filter(
                    Installment.due_date >= start_datetime,
                    Installment.due_date <= end_datetime
                )
            # If "همه اقساط", no date filter applied
            
            # Apply status filter
            status_filter_text = self.status_filter.currentText()
            if status_filter_text != "همه":
                status_map = {
                    "در انتظار": "pending",
                    "پرداخت شده": "paid",
                    "معوق": "overdue",
                    "لغو شده": "cancelled"
                }
                status = status_map.get(status_filter_text)
                if status:
                    query = query.filter(Installment.status == status)
            
            # Apply search filter
            search_text = self.search_box.text().strip()
            if search_text:
                query = query.filter(
                    (InsurancePolicy.policy_number.like(f'%{search_text}%')) |
                    (InsurancePolicy.policy_holder_name.like(f'%{search_text}%')) |
                    (InsurancePolicy.mobile_number.like(f'%{search_text}%'))
                )
            
            # Order by due date
            installments = query.order_by(Installment.due_date).all()
            
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
                    status_label = QLabel(inst.status)
                    if inst.status == 'paid':
                        status_label.setText("✓ پرداخت شده")
                        status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                    elif inst.status == 'cancelled':
                        status_label.setText("✗ لغو شده")
                        status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                    self.table.setCellWidget(row, 6, status_label)
            
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
