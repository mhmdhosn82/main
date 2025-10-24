#!/usr/bin/env python3
"""
Iran Insurance Installment Management Software - Hasnabadi 37751
Main entry point for the application.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt
from src.database.db import get_database
from src.ui.main_window import MainWindow


def setup_font():
    """Setup Vazir font for the application."""
    # Try to load Vazir font if available
    # For now, use a system font that supports Persian
    font = QFont()
    font.setFamily("Tahoma")  # Fallback to Tahoma which supports Persian
    font.setPointSize(10)
    return font


def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("نرم‌افزار مدیریت اقساط بیمه ایران - حسن‌آبادی 37751")
    app.setOrganizationName("Hasnabadi 37751")
    
    # Set RTL layout direction for Persian
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Setup font
    font = setup_font()
    app.setFont(font)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application stylesheet for professional look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #ecf0f1;
        }
        QWidget {
            font-family: Tahoma, Arial, sans-serif;
        }
        QTableWidget {
            gridline-color: #bdc3c7;
        }
        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        QPushButton {
            font-weight: bold;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
    """)
    
    # Initialize database
    db = get_database()
    
    # Create and show main window
    main_window = MainWindow(db)
    main_window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
