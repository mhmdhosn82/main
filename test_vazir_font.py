#!/usr/bin/env python3
"""Test Vazir font loading"""
import sys
import os

# Suppress Qt warnings in headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_vazir_font_loading():
    """Test that Vazir fonts can be loaded successfully"""
    print("=" * 70)
    print("Vazir Font Loading Test")
    print("=" * 70)
    print()
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont, QFontDatabase
        
        app = QApplication(sys.argv)
        
        print("1. Testing font file existence...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, 'assets')
        
        font_files = [
            'Vazir-Regular.ttf',
            'Vazir-Bold.ttf',
            'Vazir-Medium.ttf',
            'Vazir-Light.ttf'
        ]
        
        all_exist = True
        for font_file in font_files:
            font_path = os.path.join(assets_dir, font_file)
            exists = os.path.exists(font_path)
            status = "✓" if exists else "✗"
            print(f"   {status} {font_file}: {font_path}")
            if exists:
                size = os.path.getsize(font_path)
                print(f"      Size: {size:,} bytes")
            if not exists:
                all_exist = False
        
        if not all_exist:
            print("\n   ✗ Some font files are missing!")
            return False
        
        print("\n2. Testing font loading with QFontDatabase...")
        font_loaded = False
        loaded_fonts = []
        font_family_name = None
        
        for font_file in font_files:
            font_path = os.path.join(assets_dir, font_file)
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    print(f"   ✓ Loaded {font_file}: {font_families}")
                    loaded_fonts.extend(font_families)
                    font_loaded = True
                    if font_family_name is None:
                        font_family_name = font_families[0]
                else:
                    print(f"   ✗ No font families for {font_file}")
            else:
                print(f"   ✗ Failed to load {font_file}")
        
        if not font_loaded:
            print("\n   ✗ Failed to load any fonts!")
            return False
        
        print("\n3. Testing Vazir font availability...")
        available_fonts = QFontDatabase().families()
        vazir_fonts = [f for f in available_fonts if 'Vazir' in f]
        
        if vazir_fonts:
            print(f"   ✓ Vazir fonts available: {vazir_fonts}")
        else:
            print(f"   ✗ No Vazir fonts found in available fonts")
            print(f"   Available fonts: {available_fonts[:10]}...")
            return False
        
        print(f"\n4. Testing QFont creation with {font_family_name}...")
        font = QFont(font_family_name, 10)
        print(f"   ✓ Created QFont with family: {font.family()}")
        print(f"      Point size: {font.pointSize()}")
        print(f"      Weight: {font.weight()}")
        
        print("\n5. Testing application of font to QApplication...")
        app.setFont(font)
        app_font = app.font()
        print(f"   ✓ Application font family: {app_font.family()}")
        print(f"      Point size: {app_font.pointSize()}")
        
        # Verify that the font family contains "Vazir"
        if 'Vazir' in app_font.family():
            print(f"   ✓ Confirmed: Application is using a Vazir font variant")
        else:
            print(f"   ⚠ Warning: Application font might not be Vazir: {app_font.family()}")
        
        print("\n" + "=" * 70)
        print("✓ All Vazir font loading tests passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_vazir_font_loading()
    sys.exit(0 if success else 1)
