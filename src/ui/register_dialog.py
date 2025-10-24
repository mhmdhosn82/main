"""Registration dialog"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class RegisterDialog(QDialog):
    """User registration dialog"""
    
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
        self.setLayoutDirection(Qt.RightToLeft)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("ثبت‌نام کاربر جدید")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("ثبت‌نام کاربر جدید")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Full name
        layout.addWidget(QLabel("نام و نام خانوادگی:"))
        self.fullname_input = QLineEdit()
        self.fullname_input.setMinimumHeight(35)
        self.fullname_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.fullname_input)
        
        # Username
        layout.addWidget(QLabel("نام کاربری:"))
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(35)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        layout.addWidget(QLabel("رمز عبور:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.password_input)
        
        # Confirm password
        layout.addWidget(QLabel("تکرار رمز عبور:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.confirm_password_input)
        
        # Email
        layout.addWidget(QLabel("ایمیل (اختیاری):"))
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(35)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.email_input)
        
        # Phone
        layout.addWidget(QLabel("شماره تلفن (اختیاری):"))
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(35)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.phone_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("ثبت‌نام")
        register_btn.setMinimumHeight(40)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def handle_register(self):
        """Handle registration"""
        fullname = self.fullname_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text().strip() or None
        phone = self.phone_input.text().strip() or None
        
        # Validation
        if not fullname or not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدهای ضروری را پر کنید")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "خطا", "رمز عبور و تکرار آن یکسان نیست")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل 6 کاراکتر باشد")
            return
        
        # Register user
        success, message, user = self.auth_controller.register_user(
            username=username,
            password=password,
            full_name=fullname,
            email=email,
            phone=phone
        )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "خطا در ثبت‌نام", message)
