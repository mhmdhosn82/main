"""SMS settings dialog"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                            QPushButton, QMessageBox, QLabel)
from PyQt5.QtCore import Qt

class SMSSettingsDialog(QDialog):
    """Dialog for SMS API settings"""
    
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("تنظیمات پیامک")
        self.setMinimumWidth(400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        title = QLabel("پیکربندی سرویس پیامک")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        form = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("کلید API خود را وارد کنید")
        form.addRow("API Key:", self.api_key_input)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("مثال: https://api.sms-provider.com")
        form.addRow("API URL:", self.api_url_input)
        
        layout.addLayout(form)
        
        # Buttons
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """Save settings"""
        api_key = self.api_key_input.text()
        api_url = self.api_url_input.text()
        
        if not api_key or not api_url:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
        
        # In a real app, you'd save these to a config file or database
        QMessageBox.information(self, "موفق", "تنظیمات ذخیره شد")
        self.accept()
