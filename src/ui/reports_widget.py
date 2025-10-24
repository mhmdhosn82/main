"""Reports widget for custom report generation"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QComboBox, QDateEdit, QMessageBox,
                            QFileDialog, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReportsWidget(QWidget):
    """Custom reports interface"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("گزارش‌ساز")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Report type selection
        type_group = QGroupBox("نوع گزارش")
        type_layout = QFormLayout()
        
        self.report_type = QComboBox()
        self.report_type.addItems([
            "گزارش اقساط",
            "خلاصه بیمه‌نامه‌ها",
            "آمار پرداخت‌ها"
        ])
        type_layout.addRow("نوع:", self.report_type)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Filters
        filter_group = QGroupBox("فیلترها")
        filter_layout = QFormLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        filter_layout.addRow("از تاریخ:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addRow("تا تاریخ:", self.end_date)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "پرداخت شده", "در انتظار", "معوق"])
        filter_layout.addRow("وضعیت:", self.status_filter)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        excel_btn = QPushButton("📊 خروجی Excel")
        excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        excel_btn.clicked.connect(self.export_excel)
        export_layout.addWidget(excel_btn)
        
        csv_btn = QPushButton("📄 خروجی CSV")
        csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        csv_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(csv_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def export_excel(self):
        """Export report to Excel"""
        self._export_report('excel')
    
    def export_csv(self):
        """Export report to CSV"""
        self._export_report('csv')
    
    def _export_report(self, format_type):
        """Export report in specified format"""
        from ..utils import ReportGenerator
        
        try:
            # Get parameters
            report_type = self.report_type.currentText()
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            status = self.status_filter.currentText()
            
            # Map status
            status_map = {
                "همه": None,
                "پرداخت شده": "paid",
                "در انتظار": "pending",
                "معوق": "overdue"
            }
            status_filter = status_map.get(status)
            
            # Generate report
            report_gen = ReportGenerator(self.session)
            
            if "اقساط" in report_type:
                df = report_gen.generate_installment_report(
                    start_date=start_date,
                    end_date=end_date,
                    status=status_filter
                )
            elif "بیمه‌نامه" in report_type:
                df = report_gen.generate_policy_summary(self.user.id)
            else:
                df = report_gen.generate_payment_statistics(start_date, end_date)
            
            if df.empty:
                QMessageBox.information(self, "اطلاعات", "داده‌ای برای گزارش یافت نشد")
                return
            
            # Get save file name
            if format_type == 'excel':
                filename, _ = QFileDialog.getSaveFileName(
                    self, "ذخیره گزارش", "", "Excel Files (*.xlsx)"
                )
                if filename:
                    if report_gen.export_to_excel(df, filename):
                        QMessageBox.information(self, "موفق", f"گزارش در {filename} ذخیره شد")
            else:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "ذخیره گزارش", "", "CSV Files (*.csv)"
                )
                if filename:
                    if report_gen.export_to_csv(df, filename):
                        QMessageBox.information(self, "موفق", f"گزارش در {filename} ذخیره شد")
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در خروجی گزارش: {str(e)}")
