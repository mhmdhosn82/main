#!/usr/bin/env python3
"""Visual demonstration of Vazir font in PyQt application"""
import sys
import os

# Use offscreen platform for headless rendering
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def main():
    """Create a simple PyQt window showing Persian text with Vazir font"""
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QFontDatabase
    
    # Create application
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Load Vazir fonts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, 'assets')
    
    font_files = [
        'Vazir-Regular.ttf',
        'Vazir-Bold.ttf',
        'Vazir-Medium.ttf',
        'Vazir-Light.ttf'
    ]
    
    font_family_name = None
    for font_file in font_files:
        font_path = os.path.join(assets_dir, font_file)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families and font_family_name is None:
                    font_family_name = font_families[0]
    
    # Apply font globally
    if font_family_name:
        font = QFont(font_family_name, 11)
        app.setFont(font)
        print(f"✓ Applied font: {font_family_name}")
    else:
        print("✗ Failed to load fonts")
        return 1
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("نمایش فونت وزیر در PyQt")
    window.setMinimumSize(600, 400)
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout()
    layout.setSpacing(20)
    
    # Title
    title = QLabel("فونت وزیر در PyQt")
    title.setFont(QFont(font_family_name, 24, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #2c3e50; padding: 20px;")
    layout.addWidget(title)
    
    # Sample Persian text
    samples = [
        ("متن نمونه با فونت عادی", 12, QFont.Normal),
        ("متن نمونه با فونت ضخیم", 12, QFont.Bold),
        ("سیستم مدیریت اقساط بیمه ایران", 14, QFont.Normal),
        ("فونت وزیر برای نمایش بهتر متن فارسی طراحی شده است", 11, QFont.Normal),
    ]
    
    for text, size, weight in samples:
        label = QLabel(text)
        label.setFont(QFont(font_family_name, size, weight))
        label.setAlignment(Qt.AlignRight)
        label.setStyleSheet("padding: 10px; background: #ecf0f1; border-radius: 5px;")
        layout.addWidget(label)
    
    # Font info
    info_label = QLabel(f"خانواده فونت: {font_family_name}")
    info_label.setFont(QFont(font_family_name, 10))
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
    layout.addWidget(info_label)
    
    layout.addStretch()
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Style the window
    window.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f5f7fa, stop:1 #e8ecf1);
        }
    """)
    
    # Take screenshot
    window.show()
    app.processEvents()
    
    # Save screenshot
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap
    
    pixmap = window.grab()
    screenshot_path = os.path.join(base_dir, 'vazir_font_demo.png')
    pixmap.save(screenshot_path)
    print(f"✓ Screenshot saved: {screenshot_path}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
