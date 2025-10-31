#!/usr/bin/env python3
"""Test Vazir font integration in the application"""
import sys
import os

# Suppress Qt warnings in headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_app_font_integration():
    """Test that the application loads and applies Vazir font correctly"""
    print("=" * 70)
    print("Application Font Integration Test")
    print("=" * 70)
    print()
    
    try:
        # Add the project root to the path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        print("1. Testing imports...")
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QFontDatabase
        print("   ✓ PyQt5 imports successful")
        
        print("\n2. Creating QApplication...")
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)
        app.setStyle('Fusion')
        print("   ✓ QApplication created")
        
        print("\n3. Testing load_vazir_font() function from main.py...")
        # Import the load_vazir_font function
        import main as main_module
        font_loaded, font_family_name = main_module.load_vazir_font()
        
        if font_loaded and font_family_name:
            print(f"   ✓ Font loaded successfully: {font_family_name}")
        else:
            print(f"   ✗ Font loading failed")
            return False
        
        print("\n4. Applying font to QApplication...")
        font = QFont(font_family_name, 10)
        app.setFont(font)
        print(f"   ✓ Font applied to application")
        
        print("\n5. Verifying application font...")
        app_font = app.font()
        print(f"   Font family: {app_font.family()}")
        print(f"   Point size: {app_font.pointSize()}")
        
        if 'Vazir' in app_font.family():
            print(f"   ✓ Application is using Vazir font variant")
        else:
            print(f"   ✗ Application is not using Vazir font: {app_font.family()}")
            return False
        
        print("\n6. Testing font availability for widgets...")
        from PyQt5.QtWidgets import QLabel
        test_label = QLabel("تست فونت فارسی")
        test_label_font = test_label.font()
        print(f"   QLabel font family: {test_label_font.family()}")
        
        if 'Vazir' in test_label_font.family():
            print(f"   ✓ Widgets inherit Vazir font")
        else:
            print(f"   ⚠ Widget might not inherit Vazir font: {test_label_font.family()}")
        
        print("\n7. Verifying all font variants are available...")
        available_fonts = QFontDatabase().families()
        vazir_fonts = [f for f in available_fonts if 'Vazir' in f]
        print(f"   Available Vazir font variants: {vazir_fonts}")
        
        if len(vazir_fonts) >= 1:
            print(f"   ✓ {len(vazir_fonts)} Vazir font variant(s) available")
        else:
            print(f"   ✗ No Vazir fonts available")
            return False
        
        print("\n" + "=" * 70)
        print("✓ All application font integration tests passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_font_integration()
    sys.exit(0 if success else 1)
