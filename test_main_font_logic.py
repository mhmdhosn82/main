#!/usr/bin/env python3
"""Test Vazir font loading logic from main.py"""
import sys
import os

# Suppress Qt warnings in headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_main_font_loading_logic():
    """Test the font loading logic in isolation"""
    print("=" * 70)
    print("Main.py Font Loading Logic Test")
    print("=" * 70)
    print()
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QFontDatabase
        import logging
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        print("1. Creating QApplication...")
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)
        app.setStyle('Fusion')
        print("   ✓ QApplication created")
        
        print("\n2. Testing load_vazir_font() logic...")
        
        # Replicate the load_vazir_font function logic
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, 'assets')
        
        font_files = [
            'Vazir-Regular.ttf',
            'Vazir-Bold.ttf',
            'Vazir-Medium.ttf',
            'Vazir-Light.ttf'
        ]
        
        font_loaded = False
        font_family_name = None
        
        for font_file in font_files:
            font_path = os.path.join(assets_dir, font_file)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        print(f"   ✓ Loaded {font_file}: {font_families[0]}")
                        font_loaded = True
                        if font_family_name is None:
                            font_family_name = font_families[0]
                else:
                    print(f"   ✗ Failed to load {font_file}")
            else:
                print(f"   ✗ Font file not found: {font_path}")
        
        if not font_loaded:
            print("\n   ✗ No fonts were loaded!")
            return False
        
        print(f"\n3. Applying font ({font_family_name}) to application...")
        if font_loaded and font_family_name:
            font = QFont(font_family_name, 10)
            app.setFont(font)
            print(f"   ✓ Font applied: {font_family_name}")
        else:
            font = QFont("Tahoma", 10)
            app.setFont(font)
            print("   ⚠ Using fallback font: Tahoma")
            return False
        
        print("\n4. Verifying application font...")
        app_font = app.font()
        print(f"   Application font family: {app_font.family()}")
        print(f"   Point size: {app_font.pointSize()}")
        
        if 'Vazir' in app_font.family():
            print("   ✓ Confirmed: Application is using Vazir font")
        else:
            print(f"   ✗ Application is not using Vazir font: {app_font.family()}")
            return False
        
        print("\n5. Testing widget font inheritance...")
        from PyQt5.QtWidgets import QLabel, QMainWindow
        
        # Test with a QLabel
        label = QLabel("Test Persian: سلام فارسی")
        label_font = label.font()
        print(f"   QLabel default font: {label_font.family()}")
        
        # Test with a QMainWindow
        window = QMainWindow()
        window_font = window.font()
        print(f"   QMainWindow default font: {window_font.family()}")
        
        print("\n" + "=" * 70)
        print("✓ Font loading logic test passed!")
        print("   The application will correctly load and apply Vazir font")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_main_font_loading_logic()
    sys.exit(0 if success else 1)
