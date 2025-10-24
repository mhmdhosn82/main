"""Persian Date Edit Widget - A date input field with Persian calendar"""
from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, QHBoxLayout, 
                            QDialog, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from .calendar_widget import PersianCalendarWidget
import logging

logger = logging.getLogger(__name__)


class PersianDateEdit(QWidget):
    """Date input widget that displays Persian dates and shows Persian calendar popup"""
    
    dateChanged = pyqtSignal(QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._qdate = QDate.currentDate()
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Text input for displaying date
        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)
        self.date_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.date_input.setLayoutDirection(Qt.RightToLeft)
        
        # Calendar popup button
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setMaximumWidth(40)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #21618c;
            }
        """)
        self.calendar_btn.clicked.connect(self.show_calendar_dialog)
        
        layout.addWidget(self.date_input)
        layout.addWidget(self.calendar_btn)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Update the display with current Persian date"""
        if self._qdate:
            # Convert to Persian
            date = self._qdate.toPyDate()
            jalali = JalaliDateTime.to_jalali(datetime(date.year, date.month, date.day))
            
            # Format: year/month/day
            persian_date = f"{jalali.year}/{jalali.month:02d}/{jalali.day:02d}"
            
            # Get month name
            month_names = {
                1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
                4: 'تیر', 5: 'مرداد', 6: 'شهریور',
                7: 'مهر', 8: 'آبان', 9: 'آذر',
                10: 'دی', 11: 'بهمن', 12: 'اسفند'
            }
            month_name = month_names.get(jalali.month, '')
            
            # Display with Persian digits
            from ..utils.persian_utils import format_persian_number
            display_text = f"{format_persian_number(jalali.day)} {month_name} {format_persian_number(jalali.year)}"
            
            self.date_input.setText(display_text)
    
    def show_calendar_dialog(self):
        """Show calendar picker dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("انتخاب تاریخ")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("انتخاب تاریخ شمسی")
        title.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                padding: 10px;
                border-radius: 5px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Persian calendar
        calendar = PersianCalendarWidget()
        calendar.dateClicked.connect(lambda qdate: self.set_date_from_dialog(qdate, dialog))
        
        # Set current date in calendar
        date = self._qdate.toPyDate()
        jalali = JalaliDateTime.to_jalali(datetime(date.year, date.month, date.day))
        calendar.current_jalali = JalaliDateTime(jalali.year, jalali.month, 1)
        calendar.update_calendar()
        
        layout.addWidget(calendar)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        today_btn = QPushButton("امروز")
        today_btn.setStyleSheet("""
            QPushButton {
                background: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #27ae60; }
        """)
        today_btn.clicked.connect(lambda: self.set_date_from_dialog(QDate.currentDate(), dialog))
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(today_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def set_date_from_dialog(self, qdate, dialog):
        """Set date from calendar dialog selection"""
        self.setDate(qdate)
        dialog.accept()
    
    def date(self):
        """Get current date as QDate"""
        return self._qdate
    
    def setDate(self, qdate):
        """Set current date from QDate"""
        if qdate != self._qdate:
            self._qdate = qdate
            self.update_display()
            self.dateChanged.emit(qdate)
    
    def setDisplayFormat(self, format_str):
        """Compatibility method - format is always Persian"""
        pass
    
    def setCalendarPopup(self, popup):
        """Compatibility method - always has calendar popup"""
        pass
