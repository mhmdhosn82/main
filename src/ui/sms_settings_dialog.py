"""SMS settings dialog"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                            QPushButton, QMessageBox, QLabel, QCheckBox)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class SMSSettingsDialog(QDialog):
    """Dialog for SMS API settings"""
    
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("تنظیمات پیامک")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        title = QLabel("پیکربندی سرویس پیامک")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        desc = QLabel("برای فعال‌سازی سرویس ارسال پیامک یادآوری، اطلاعات API را وارد کنید.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(desc)
        
        form = QFormLayout()
        
        self.enabled_checkbox = QCheckBox("فعال‌سازی سرویس پیامک")
        form.addRow(self.enabled_checkbox)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("کلید API خود را وارد کنید")
        form.addRow("API Key:", self.api_key_input)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("مثال: https://api.sms-provider.com")
        form.addRow("API URL:", self.api_url_input)
        
        self.sender_input = QLineEdit()
        self.sender_input.setPlaceholderText("شماره ارسال‌کننده (اختیاری)")
        form.addRow("شماره ارسال‌کننده:", self.sender_input)
        
        layout.addLayout(form)
        
        # Test button
        test_btn = QPushButton("تست اتصال")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        # Buttons
        btn_layout = QFormLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addRow(save_btn, cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load saved settings"""
        try:
            from ..utils import get_config
            config = get_config()
            sms_config = config.get_sms_config()
            
            self.enabled_checkbox.setChecked(sms_config.get('enabled', False))
            self.api_key_input.setText(sms_config.get('api_key', ''))
            self.api_url_input.setText(sms_config.get('api_url', ''))
            self.sender_input.setText(sms_config.get('sender_number', ''))
        except Exception as e:
            logger.error(f"Failed to load SMS settings: {e}")
    
    def test_connection(self):
        """Test SMS API connection"""
        api_key = self.api_key_input.text().strip()
        api_url = self.api_url_input.text().strip()
        
        if not api_key or not api_url:
            QMessageBox.warning(self, "خطا", "لطفاً API Key و API URL را وارد کنید")
            return
        
        # Simple validation
        if not api_url.startswith('http'):
            QMessageBox.warning(self, "خطا", "API URL باید با http یا https شروع شود")
            return
        
        QMessageBox.information(
            self, 
            "اطلاعات", 
            "در نسخه فعلی، تست اتصال واقعی به API پیامک پیاده‌سازی نشده است.\n"
            "پس از ذخیره، سیستم از این تنظیمات برای ارسال پیامک استفاده خواهد کرد."
        )
    
    def save_settings(self):
        """Save settings"""
        from ..utils import get_config
        
        api_key = self.api_key_input.text().strip()
        api_url = self.api_url_input.text().strip()
        sender = self.sender_input.text().strip()
        enabled = self.enabled_checkbox.isChecked()
        
        if enabled and (not api_key or not api_url):
            QMessageBox.warning(self, "خطا", "برای فعال‌سازی سرویس، لطفاً API Key و API URL را وارد کنید")
            return
        
        if api_url and not api_url.startswith('http'):
            QMessageBox.warning(self, "خطا", "API URL باید با http یا https شروع شود")
            return
        
        try:
            config = get_config()
            success = config.set_sms_config(api_key, api_url, sender)
            
            if success:
                QMessageBox.information(self, "موفق", "تنظیمات با موفقیت ذخیره شد")
                logger.info("SMS settings saved successfully")
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "خطا در ذخیره‌سازی تنظیمات")
        except Exception as e:
            logger.error(f"Failed to save SMS settings: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره‌سازی: {str(e)}")
