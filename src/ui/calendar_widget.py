"""Calendar widget for installments"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, QLabel,
                            QListWidget, QHBoxLayout, QMessageBox, QGridLayout,
                            QPushButton, QFrame, QComboBox, QLineEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
from datetime import datetime
import jdatetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime
import logging

logger = logging.getLogger(__name__)

class PersianCalendarWidget(QWidget):
    """Custom Persian Calendar Widget"""
    dateClicked = pyqtSignal(QDate)
    
    def __init__(self):
        super().__init__()
        self.current_jalali = JalaliDateTime.now()
        self.selected_date = None
        self.date_formats = {}  # Store formatting for dates
        self.setup_ui()
        self.update_calendar()
    
    def setup_ui(self):
        """Setup Persian calendar UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with month/year and navigation
        header_layout = QHBoxLayout()
        
        self.prev_month_btn = QPushButton("◀")
        self.prev_month_btn.setMaximumWidth(40)
        self.prev_month_btn.clicked.connect(self.previous_month)
        self.prev_month_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        self.month_year_label = QLabel()
        self.month_year_label.setAlignment(Qt.AlignCenter)
        self.month_year_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        
        self.next_month_btn = QPushButton("▶")
        self.next_month_btn.setMaximumWidth(40)
        self.next_month_btn.clicked.connect(self.next_month)
        self.next_month_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        header_layout.addWidget(self.next_month_btn)
        header_layout.addWidget(self.month_year_label, stretch=1)
        header_layout.addWidget(self.prev_month_btn)
        
        layout.addLayout(header_layout)
        
        # Calendar grid
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(2)
        
        # Weekday headers
        weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
        for col, day in enumerate(weekdays):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: #34495e;
                    color: white;
                    padding: 8px;
                    font-weight: bold;
                    border-radius: 3px;
                }
            """)
            self.calendar_grid.addWidget(label, 0, col)
        
        # Day buttons (6 rows x 7 columns)
        self.day_buttons = []
        for row in range(1, 7):
            week_buttons = []
            for col in range(7):
                btn = QPushButton()
                btn.setMinimumHeight(50)
                btn.clicked.connect(lambda checked, r=row-1, c=col: self.day_clicked(r, c))
                self.calendar_grid.addWidget(btn, row, col)
                week_buttons.append(btn)
            self.day_buttons.append(week_buttons)
        
        layout.addLayout(self.calendar_grid)
        self.setLayout(layout)
    
    def update_calendar(self):
        """Update calendar display"""
        # Update month/year label
        month_names = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        month_name = month_names.get(self.current_jalali.month, '')
        self.month_year_label.setText(f"{month_name} {self.current_jalali.year}")
        
        # Get first day of month
        first_day = JalaliDate(self.current_jalali.year, self.current_jalali.month, 1)
        
        # Get weekday of first day (Saturday = 0)
        first_weekday = first_day.weekday()
        
        # Get number of days in month
        if self.current_jalali.month <= 6:
            days_in_month = 31
        elif self.current_jalali.month <= 11:
            days_in_month = 30
        else:
            # Esfand - check for leap year
            days_in_month = 30 if first_day.is_leap() else 29
        
        # Update day buttons
        day = 1
        for row in range(6):
            for col in range(7):
                btn = self.day_buttons[row][col]
                cell_index = row * 7 + col
                
                if cell_index < first_weekday or day > days_in_month:
                    btn.setText("")
                    btn.setEnabled(False)
                    btn.setStyleSheet("background: #ecf0f1; border: none;")
                else:
                    btn.setText(str(day))
                    btn.setEnabled(True)
                    
                    # Create date for this day
                    jalali_date = JalaliDate(self.current_jalali.year, self.current_jalali.month, day)
                    gregorian_date = jalali_date.to_gregorian()
                    qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
                    
                    # Check if this date has custom formatting
                    date_key = gregorian_date
                    if date_key in self.date_formats:
                        fmt = self.date_formats[date_key]
                        bg_color = fmt.background().color()
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                                border: 2px solid #bdc3c7;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 11pt;
                            }}
                            QPushButton:hover {{
                                border: 2px solid #3498db;
                                background: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 200);
                            }}
                        """)
                    else:
                        btn.setStyleSheet("""
                            QPushButton {
                                background: white;
                                border: 1px solid #bdc3c7;
                                border-radius: 5px;
                                font-size: 11pt;
                            }
                            QPushButton:hover {
                                background: #d5f4e6;
                                border: 2px solid #3498db;
                            }
                        """)
                    
                    # Store the date in button property
                    btn.setProperty("qdate", qdate)
                    btn.setProperty("day", day)
                    
                    day += 1
    
    def day_clicked(self, row, col):
        """Handle day button click"""
        btn = self.day_buttons[row][col]
        qdate = btn.property("qdate")
        if qdate:
            self.selected_date = qdate
            self.dateClicked.emit(qdate)
    
    def previous_month(self):
        """Go to previous month"""
        if self.current_jalali.month == 1:
            self.current_jalali = JalaliDateTime(self.current_jalali.year - 1, 12, 1)
        else:
            self.current_jalali = JalaliDateTime(self.current_jalali.year, self.current_jalali.month - 1, 1)
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_jalali.month == 12:
            self.current_jalali = JalaliDateTime(self.current_jalali.year + 1, 1, 1)
        else:
            self.current_jalali = JalaliDateTime(self.current_jalali.year, self.current_jalali.month + 1, 1)
        self.update_calendar()
    
    def setDateTextFormat(self, qdate, fmt):
        """Set text format for a specific date"""
        date = qdate.toPyDate()
        self.date_formats[date] = fmt
        self.update_calendar()


class CalendarWidget(QWidget):
    """Calendar view for installments"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.installments_by_date = {}
        self.setup_ui()
        self.load_installments()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("تقویم اقساط شمسی")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                color: white;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Filters section
        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        filters_layout = QHBoxLayout()
        
        # Insurance type filter
        filters_layout.addWidget(QLabel("نوع بیمه:"))
        self.insurance_type_filter = QComboBox()
        self.insurance_type_filter.addItems(["همه", "شخص ثالث", "بدنه", "عمر", "حوادث", "آتش‌سوزی"])
        self.insurance_type_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.insurance_type_filter)
        
        # Status filter
        filters_layout.addWidget(QLabel("وضعیت:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "در انتظار", "پرداخت شده", "معوق"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.status_filter)
        
        # Policy number filter
        filters_layout.addWidget(QLabel("شماره بیمه‌نامه:"))
        self.policy_number_filter = QLineEdit()
        self.policy_number_filter.setPlaceholderText("جستجو...")
        self.policy_number_filter.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.policy_number_filter)
        
        # Reset filters button
        reset_btn = QPushButton("حذف فیلترها")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        reset_btn.clicked.connect(self.reset_filters)
        filters_layout.addWidget(reset_btn)
        
        filters_layout.addStretch()
        filters_frame.setLayout(filters_layout)
        layout.addWidget(filters_frame)
        
        content_layout = QHBoxLayout()
        
        # Persian Calendar
        self.calendar = PersianCalendarWidget()
        self.calendar.dateClicked.connect(self.date_selected)
        content_layout.addWidget(self.calendar)
        
        # Details panel
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        details_layout = QVBoxLayout()
        
        self.selected_date_label = QLabel("تاریخ انتخابی:")
        self.selected_date_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                background: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        details_layout.addWidget(self.selected_date_label)
        
        self.installments_list = QListWidget()
        self.installments_list.setLayoutDirection(Qt.RightToLeft)
        self.installments_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:hover {
                background: #d5f4e6;
            }
        """)
        details_layout.addWidget(self.installments_list)
        
        details_frame.setLayout(details_layout)
        details_frame.setMinimumWidth(300)
        content_layout.addWidget(details_frame)
        
        layout.addLayout(content_layout)
        
        # Legend
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(self.create_legend_item("🟢 پرداخت شده", QColor(39, 174, 96)))
        legend_layout.addWidget(self.create_legend_item("🟡 در انتظار", QColor(243, 156, 18)))
        legend_layout.addWidget(self.create_legend_item("🔴 معوق", QColor(231, 76, 60)))
        legend_layout.addStretch()
        legend_frame.setLayout(legend_layout)
        layout.addWidget(legend_frame)
        
        self.setLayout(layout)
    
    def create_legend_item(self, text, color):
        """Create legend item"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                padding: 8px 15px;
                margin: 5px;
                background: rgba({color.red()}, {color.green()}, {color.blue()}, 100);
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid rgba({color.red()}, {color.green()}, {color.blue()}, 200);
            }}
        """)
        return label
    
    def load_installments(self):
        """Load installments and mark calendar"""
        from ..controllers import InstallmentController
        from ..models import InsurancePolicy, Installment
        
        try:
            # Build query with filters
            query = self.session.query(Installment, InsurancePolicy).join(
                InsurancePolicy
            ).filter(InsurancePolicy.user_id == self.user.id)
            
            # Apply insurance type filter
            if hasattr(self, 'insurance_type_filter') and self.insurance_type_filter.currentText() != "همه":
                query = query.filter(InsurancePolicy.policy_type == self.insurance_type_filter.currentText())
            
            # Apply status filter
            if hasattr(self, 'status_filter') and self.status_filter.currentText() != "همه":
                status_map = {
                    "در انتظار": "pending",
                    "پرداخت شده": "paid",
                    "معوق": "overdue"
                }
                status = status_map.get(self.status_filter.currentText())
                if status:
                    query = query.filter(Installment.status == status)
            
            # Apply policy number filter
            if hasattr(self, 'policy_number_filter') and self.policy_number_filter.text():
                query = query.filter(InsurancePolicy.policy_number.like(f'%{self.policy_number_filter.text()}%'))
            
            installments = query.all()
            
            # Group by date
            self.installments_by_date = {}
            
            for inst, policy in installments:
                date_key = inst.due_date.date()
                if date_key not in self.installments_by_date:
                    self.installments_by_date[date_key] = []
                self.installments_by_date[date_key].append((inst, policy))
            
            # Mark dates on calendar
            self.mark_calendar_dates()
            
        except Exception as e:
            logger.error(f"Error loading installments: {e}")
    
    def mark_calendar_dates(self):
        """Mark dates with installments on calendar"""
        for date, installments in self.installments_by_date.items():
            qdate = QDate(date.year, date.month, date.day)
            
            # Determine color based on status
            has_paid = any(inst.status == 'paid' for inst, _ in installments)
            has_overdue = any(inst.status == 'overdue' for inst, _ in installments)
            has_pending = any(inst.status == 'pending' for inst, _ in installments)
            
            fmt = QTextCharFormat()
            fmt.setFontWeight(75)
            
            if has_overdue:
                fmt.setBackground(QColor(231, 76, 60, 100))
            elif has_pending:
                fmt.setBackground(QColor(243, 156, 18, 100))
            elif has_paid:
                fmt.setBackground(QColor(39, 174, 96, 100))
            
            self.calendar.setDateTextFormat(qdate, fmt)
    
    def date_selected(self, qdate):
        """Handle date selection"""
        from ..utils.persian_utils import format_currency, PersianDateConverter
        
        date = qdate.toPyDate()
        
        # Update label with Persian date
        gregorian_datetime = datetime(date.year, date.month, date.day)
        jalali_date = JalaliDateTime.to_jalali(gregorian_datetime)
        
        month_names = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        weekdays = {
            0: 'شنبه', 1: 'یکشنبه', 2: 'دوشنبه',
            3: 'سه‌شنبه', 4: 'چهارشنبه', 5: 'پنج‌شنبه', 6: 'جمعه'
        }
        
        persian_date = f"{weekdays.get(jalali_date.weekday(), '')} {jalali_date.day} {month_names.get(jalali_date.month, '')} {jalali_date.year}"
        self.selected_date_label.setText(f"تاریخ انتخابی: {persian_date}")
        
        # Clear list
        self.installments_list.clear()
        
        # Show installments for this date
        if date in self.installments_by_date:
            for inst, policy in self.installments_by_date[date]:
                # Create detailed item text with all required information
                status_persian = {
                    'pending': 'در انتظار',
                    'paid': 'پرداخت شده',
                    'overdue': 'معوق',
                    'cancelled': 'لغو شده'
                }.get(inst.status, inst.status)
                
                item_text = (
                    f"📄 شماره بیمه‌نامه: {policy.policy_number}\n"
                    f"👤 نام بیمه‌گذار: {policy.policy_holder_name}\n"
                    f"📋 نوع بیمه: {policy.policy_type or '-'}\n"
                    f"💰 مبلغ: {format_currency(inst.amount)}\n"
                    f"📱 شماره موبایل: {policy.mobile_number or '-'}\n"
                    f"🔢 شماره قسط: {inst.installment_number}\n"
                    f"📊 وضعیت: {status_persian}\n"
                    f"{'-' * 50}"
                )
                self.installments_list.addItem(item_text)
        else:
            self.installments_list.addItem("قسطی برای این تاریخ ثبت نشده است")
    
    def apply_filters(self):
        """Apply filters and reload installments"""
        self.load_installments()
    
    def reset_filters(self):
        """Reset all filters"""
        self.insurance_type_filter.setCurrentText("همه")
        self.status_filter.setCurrentText("همه")
        self.policy_number_filter.clear()
        self.load_installments()
    
    def refresh(self):
        """Refresh calendar"""
        self.load_installments()
