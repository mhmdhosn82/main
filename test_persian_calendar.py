#!/usr/bin/env python3
"""
Persian Calendar Navigation Test
Tests that the Persian calendar can navigate at least 5 years into the future
without crashing, as required by the fix for the Bahman 1404 crash issue.
"""
import sys
import os

# Suppress Qt warnings in headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDate
from persiantools.jdatetime import JalaliDateTime, JalaliDate
from src.ui.calendar_widget import PersianCalendarWidget
from src.ui.persian_date_edit import PersianDateEdit


def test_calendar_navigation():
    """Test that calendar can navigate 5 years ahead without errors"""
    print("\n" + "=" * 70)
    print("Persian Calendar Navigation Test - 5 Years Coverage")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    calendar = PersianCalendarWidget()
    
    current = JalaliDateTime.now()
    target_year = current.year + 5
    
    print(f"\nTesting calendar navigation from {current.year} to {target_year}...")
    
    # Navigate 60 months (5 years) forward
    try:
        for i in range(60):
            calendar.next_month()
            calendar.update_calendar()  # This would crash with the old bug
        
        print(f"✓ Successfully navigated 60 months forward")
        print(f"  Current position: {calendar.current_jalali.year}/{calendar.current_jalali.month:02d}")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Navigate back
    try:
        for i in range(60):
            calendar.previous_month()
            calendar.update_calendar()
        
        print(f"✓ Successfully navigated 60 months backward")
        
    except Exception as e:
        print(f"✗ FAILED on backward navigation: {e}")
        return False
    
    return True


def test_leap_year_handling():
    """Test that leap years in Esfand (month 12) are handled correctly"""
    print("\n" + "=" * 70)
    print("Leap Year Handling Test")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    calendar = PersianCalendarWidget()
    
    current = JalaliDateTime.now()
    
    # Find leap years in next 5 years
    leap_years = [y for y in range(current.year, current.year + 6) if JalaliDate.is_leap(y)]
    non_leap_years = [y for y in range(current.year, current.year + 6) if not JalaliDate.is_leap(y)]
    
    print(f"\nLeap years in range: {leap_years}")
    print(f"Non-leap years in range: {non_leap_years[:2]}")
    
    # Test leap years - Esfand should have 30 days
    for year in leap_years:
        try:
            calendar.current_jalali = JalaliDateTime(year, 12, 1)
            calendar.update_calendar()
            
            # Count enabled day buttons
            day_count = sum(1 for row in calendar.day_buttons for btn in row if btn.isEnabled() and btn.text())
            
            if day_count != 30:
                print(f"✗ FAILED: Leap year {year}/12 has {day_count} days, expected 30")
                return False
            
            print(f"✓ Leap year {year}/12 correctly shows 30 days")
            
        except Exception as e:
            print(f"✗ FAILED for leap year {year}: {e}")
            return False
    
    # Test non-leap years - Esfand should have 29 days
    for year in non_leap_years[:2]:
        try:
            calendar.current_jalali = JalaliDateTime(year, 12, 1)
            calendar.update_calendar()
            
            day_count = sum(1 for row in calendar.day_buttons for btn in row if btn.isEnabled() and btn.text())
            
            if day_count != 29:
                print(f"✗ FAILED: Non-leap year {year}/12 has {day_count} days, expected 29")
                return False
            
            print(f"✓ Non-leap year {year}/12 correctly shows 29 days")
            
        except Exception as e:
            print(f"✗ FAILED for non-leap year {year}: {e}")
            return False
    
    return True


def test_date_picker_future_dates():
    """Test that PersianDateEdit can handle dates 5 years in the future"""
    print("\n" + "=" * 70)
    print("Persian Date Picker - Future Dates Test")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    date_edit = PersianDateEdit()
    
    current = JalaliDateTime.now()
    target_year = current.year + 5
    
    print(f"\nTesting date picker with year {target_year}...")
    
    try:
        # Test setting a date 5 years in the future
        future_jalali = JalaliDate(target_year, 6, 15)
        future_gregorian = future_jalali.to_gregorian()
        future_qdate = QDate(future_gregorian.year, future_gregorian.month, future_gregorian.day)
        
        date_edit.setDate(future_qdate)
        result_qdate = date_edit.date()
        
        if result_qdate != future_qdate:
            print(f"✗ FAILED: Date mismatch")
            return False
        
        display_text = date_edit.date_input.text()
        print(f"✓ Successfully set and displayed date {target_year}/06/15")
        print(f"  Display: {display_text}")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def run_all_tests():
    """Run all Persian calendar tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PERSIAN CALENDAR TEST SUITE" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")
    
    tests = [
        ("Navigation Test", test_calendar_navigation),
        ("Leap Year Test", test_leap_year_handling),
        ("Date Picker Test", test_date_picker_future_dates),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✓ All tests passed! Persian calendar supports 5+ years ahead.")
        print("  The calendar can navigate without crashes and correctly handles:")
        print("    • Forward/backward navigation")
        print("    • Leap year detection in Esfand (month 12)")
        print("    • Date picker for future dates")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
