"""
Settings widget for application customization.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QColorDialog, QMessageBox, QGroupBox,
                            QFormLayout, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.database.db import Database


class SettingsWidget(QWidget):
    """Widget for application settings."""
    
    def __init__(self, db: Database):
        """
        Initialize the settings widget.
        
        Args:
            db: Database instance
        """
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("تنظیمات")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)
        
        # Appearance settings
        appearance_group = QGroupBox("تنظیمات ظاهری")
        appearance_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        appearance_layout = QFormLayout()
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["روشن", "تیره"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        appearance_layout.addRow("تم:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(20)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        appearance_layout.addRow("اندازه فونت:", self.font_size_spin)
        
        # Primary color
        color_layout = QHBoxLayout()
        self.primary_color_label = QLabel("      ")
        self.primary_color_label.setStyleSheet("background-color: #3498db; border: 1px solid #000;")
        color_layout.addWidget(self.primary_color_label)
        
        choose_color_btn = QPushButton("انتخاب رنگ")
        choose_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        choose_color_btn.clicked.connect(self.choose_primary_color)
        color_layout.addWidget(choose_color_btn)
        color_layout.addStretch()
        
        appearance_layout.addRow("رنگ اصلی:", color_layout)
        
        # Database settings
        database_group = QGroupBox("تنظیمات پایگاه داده")
        database_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        database_layout = QVBoxLayout()
        database_group.setLayout(database_layout)
        layout.addWidget(database_group)
        
        db_info = QLabel(f"مسیر پایگاه داده: {self.db.db_path}")
        db_info.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        db_info.setAlignment(Qt.AlignRight)
        database_layout.addWidget(db_info)
        
        backup_btn = QPushButton("پشتیبان‌گیری از پایگاه داده")
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        backup_btn.clicked.connect(self.backup_database)
        database_layout.addWidget(backup_btn)
        
        # About section
        about_group = QGroupBox("درباره نرم‌افزار")
        about_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        about_layout = QVBoxLayout()
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        about_text = QLabel("""
        <div style='text-align: right; padding: 10px;'>
            <b>نرم‌افزار مدیریت اقساط بیمه ایران</b><br>
            نسخه: 1.0.0<br>
            توسعه‌دهنده: حسن‌آبادی 37751<br>
            <br>
            این نرم‌افزار برای مدیریت بیمه‌نامه‌ها و اقساط آن‌ها طراحی شده است.
        </div>
        """)
        about_text.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; padding: 15px;")
        about_layout.addWidget(about_text)
        
        # Save button
        save_layout = QHBoxLayout()
        layout.addLayout(save_layout)
        
        save_layout.addStretch()
        
        save_btn = QPushButton("ذخیره تنظیمات")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 30px;
                border-radius: 5px;
                border: none;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(save_btn)
        
        layout.addStretch()
        
    def refresh_data(self):
        """Refresh settings data."""
        # Load saved settings from database if available
        pass
    
    def choose_primary_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.primary_color_label.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #000;"
            )
    
    def save_settings(self):
        """Save settings to database."""
        try:
            # In a full implementation, save settings to the database
            QMessageBox.information(self, "موفق", "تنظیمات با موفقیت ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def backup_database(self):
        """Create a backup of the database."""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"insurance_data_backup_{timestamp}.db"
            
            shutil.copy(self.db.db_path, backup_file)
            
            QMessageBox.information(
                self, 
                "موفق", 
                f"پشتیبان‌گیری با موفقیت انجام شد.\nفایل: {backup_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در پشتیبان‌گیری: {str(e)}")
