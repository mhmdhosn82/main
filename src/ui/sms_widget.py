"""SMS reminder widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTextEdit, QLineEdit, QTableWidget,
                            QTableWidgetItem, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class SMSWidget(QWidget):
    """SMS reminder management interface"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.load_reminders()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("مدیریت پیامک‌های یادآوری")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # SMS configuration section
        config_group = QGroupBox("پیکربندی سرویس پیامک")
        config_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("کلید API")
        config_layout.addRow("API Key:", self.api_key_input)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("آدرس API")
        config_layout.addRow("API URL:", self.api_url_input)
        
        save_config_btn = QPushButton("ذخیره تنظیمات")
        save_config_btn.clicked.connect(self.save_sms_config)
        config_layout.addRow(save_config_btn)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Send SMS section
        send_group = QGroupBox("ارسال پیامک")
        send_layout = QVBoxLayout()
        
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("شماره تلفن:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09123456789")
        phone_layout.addWidget(self.phone_input)
        send_layout.addLayout(phone_layout)
        
        send_layout.addWidget(QLabel("متن پیام:"))
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("متن پیامک را وارد کنید...")
        send_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("📱 ارسال پیامک")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        send_btn.clicked.connect(self.send_sms)
        send_layout.addWidget(send_btn)
        
        send_group.setLayout(send_layout)
        layout.addWidget(send_group)
        
        # Reminder history table
        history_label = QLabel("تاریخچه یادآورها")
        history_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(history_label)
        
        self.reminders_table = QTableWidget()
        self.reminders_table.setColumnCount(5)
        self.reminders_table.setHorizontalHeaderLabels([
            "نوع", "عنوان", "تاریخ ارسال", "گیرنده", "وضعیت"
        ])
        self.reminders_table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.reminders_table)
        
        # Auto-schedule button
        auto_btn = QPushButton("🤖 برنامه‌ریزی خودکار یادآورها")
        auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        auto_btn.clicked.connect(self.auto_schedule_reminders)
        layout.addWidget(auto_btn)
        
        self.setLayout(layout)
    
    def save_sms_config(self):
        """Save SMS API configuration"""
        api_key = self.api_key_input.text()
        api_url = self.api_url_input.text()
        
        if not api_key or not api_url:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
        
        from ..utils import SMSManager
        sms_manager = SMSManager()
        sms_manager.configure(api_key, api_url)
        
        QMessageBox.information(self, "موفق", "تنظیمات ذخیره شد")
    
    def send_sms(self):
        """Send SMS message"""
        from ..utils import SMSManager
        
        phone = self.phone_input.text()
        message = self.message_input.toPlainText()
        
        if not phone or not message:
            QMessageBox.warning(self, "خطا", "لطفاً شماره تلفن و متن پیام را وارد کنید")
            return
        
        sms_manager = SMSManager(
            self.api_key_input.text(),
            self.api_url_input.text()
        )
        
        success, response = sms_manager.send_sms(phone, message)
        
        if success:
            QMessageBox.information(self, "موفق", "پیامک با موفقیت ارسال شد")
            self.phone_input.clear()
            self.message_input.clear()
            self.load_reminders()
        else:
            QMessageBox.warning(self, "خطا", f"خطا در ارسال پیامک: {response.get('error', 'خطای نامشخص')}")
    
    def load_reminders(self):
        """Load reminder history"""
        from ..controllers import ReminderController
        from ..utils.persian_utils import PersianDateConverter
        
        try:
            controller = ReminderController(self.session)
            reminders = controller.get_user_reminders(self.user.id)
            
            self.reminders_table.setRowCount(len(reminders))
            
            for row, reminder in enumerate(reminders):
                self.reminders_table.setItem(row, 0, QTableWidgetItem(reminder.reminder_type))
                self.reminders_table.setItem(row, 1, QTableWidgetItem(reminder.title or "-"))
                
                sent_date = "-"
                if reminder.sent_date:
                    sent_date = PersianDateConverter.gregorian_to_jalali(reminder.sent_date)
                self.reminders_table.setItem(row, 2, QTableWidgetItem(sent_date))
                
                self.reminders_table.setItem(row, 3, QTableWidgetItem(reminder.recipient_phone or "-"))
                self.reminders_table.setItem(row, 4, QTableWidgetItem(reminder.status))
            
            self.reminders_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
    
    def auto_schedule_reminders(self):
        """Auto-schedule reminders for all policies"""
        from ..controllers import ReminderController, PolicyController
        
        try:
            policy_ctrl = PolicyController(self.session)
            reminder_ctrl = ReminderController(self.session)
            
            policies = policy_ctrl.get_all_policies(self.user.id, status='active')
            
            total_scheduled = 0
            for policy in policies:
                success, count = reminder_ctrl.auto_schedule_reminders_for_policy(policy.id)
                if success:
                    total_scheduled += count
            
            QMessageBox.information(
                self,
                "موفق",
                f"{total_scheduled} یادآور به صورت خودکار برنامه‌ریزی شد"
            )
            self.load_reminders()
            
        except Exception as e:
            logger.error(f"Error auto-scheduling reminders: {e}")
            QMessageBox.warning(self, "خطا", "خطا در برنامه‌ریزی خودکار")
