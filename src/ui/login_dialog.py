"""Login dialog with Persian UI"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Login dialog for user authentication"""
    
    login_successful = pyqtSignal(object)  # Emits user object on successful login
    
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
        self.apply_rtl()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("ورود به سیستم - مدیریت اقساط بیمه ایران")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("سیستم مدیریت اقساط بیمه")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("لطفاً وارد حساب کاربری خود شوید")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                padding: 5px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Username field
        username_label = QLabel("نام کاربری:")
        username_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(35)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("رمز عبور:")
        password_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Login button
        self.login_button = QPushButton("ورود")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)
        
        # Register button
        self.register_button = QPushButton("ثبت‌نام")
        self.register_button.setMinimumHeight(40)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """)
        self.register_button.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def apply_rtl(self):
        """Apply right-to-left layout for Persian"""
        self.setLayoutDirection(Qt.RightToLeft)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری و رمز عبور را وارد کنید")
            return
        
        # Attempt login
        success, message, user = self.auth_controller.login(username, password)
        
        if success:
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, "خطا در ورود", message)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_register_dialog(self):
        """Show registration dialog"""
        from .register_dialog import RegisterDialog
        
        dialog = RegisterDialog(self.auth_controller, self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(
                self,
                "ثبت‌نام موفق",
                "ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید."
            )
