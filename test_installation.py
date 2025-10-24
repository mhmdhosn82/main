#!/usr/bin/env python3
"""
Test script to verify the installation of Iran Insurance Management Software.
Run this script after installation to ensure everything is working correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported."""
    print("Testing module imports...")
    
    try:
        from src.models import init_database, get_session, User, InsurancePolicy, Installment, Reminder
        from src.controllers import AuthController, PolicyController, InstallmentController, ReminderController
        from src.utils.persian_utils import PersianDateConverter, format_currency
        print("✓ All core modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.ui import LoginDialog, MainWindow, DashboardWidget, PolicyWidget
        print("✓ UI modules imported successfully")
    except ImportError as e:
        print(f"✗ UI import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    
    try:
        from src.models import init_database, get_session, User, InsurancePolicy, Installment
        from src.controllers import PolicyController, InstallmentController
        from src.utils.persian_utils import PersianDateConverter
        from datetime import datetime
        
        # Initialize database
        init_database()
        session = get_session()
        
        # Create test user if not exists
        test_user = session.query(User).filter_by(username='test_verify').first()
        if not test_user:
            from src.controllers import AuthController
            auth_ctrl = AuthController(session)
            success, message, test_user = auth_ctrl.register_user(
                username='test_verify',
                password='test123',
                full_name='کاربر تست',
                email='test@test.com',
                phone='09120000000',
                role='user'
            )
            if not success:
                print(f"✗ Failed to create test user: {message}")
                session.close()
                return False
        
        # Create test policy using controller
        policy_ctrl = PolicyController(session)
        
        test_date = datetime.now()
        end_date = datetime(test_date.year + 1, test_date.month, test_date.day)
        
        policy_data = {
            'policy_number': f'TEST-VERIFY-{datetime.now().timestamp()}',
            'policy_holder_name': 'بیمه‌شده تست',
            'policy_holder_national_id': '1234567890',
            'policy_type': 'Life',
            'insurance_company': 'بیمه ایران',
            'total_amount': 10000000,
            'start_date': test_date,
            'end_date': end_date,
            'description': 'بیمه‌نامه تست'
        }
        
        success, message, policy = policy_ctrl.create_policy(test_user.id, policy_data)
        
        if not success:
            print(f"✗ Failed to create policy: {message}")
            session.close()
            return False
        
        print(f"✓ Policy created with ID: {policy.id}")
        
        # Check installments
        installment_ctrl = InstallmentController(session)
        installments = installment_ctrl.get_policy_installments(policy.id)
        
        print(f"✓ Retrieved {len(installments)} installments")
        
        # Get statistics
        stats = policy_ctrl.get_policy_statistics(test_user.id)
        print(f"✓ Statistics retrieved: total_policies={stats['total_policies']}")
        
        # Clean up
        session.delete(policy)
        session.delete(test_user)
        session.commit()
        print("✓ Test data cleaned up")
        
        session.close()
        
        # Clean up database file
        if os.path.exists('insurance.db'):
            os.remove('insurance.db')
        
        return True
    except Exception as e:
        print(f"✗ Database test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from src.utils.persian_utils import PersianDateConverter, format_currency
        from datetime import datetime
        
        # Test date functions
        converter = PersianDateConverter()
        
        # Test Gregorian to Jalali
        test_date = datetime.now()
        jalali = converter.gregorian_to_jalali(test_date)
        print(f"✓ Current Jalali date: {jalali}")
        
        # Test Jalali to Gregorian
        greg = converter.jalali_to_gregorian(1402, 6, 15)
        if greg:
            print(f"✓ Jalali to Gregorian conversion works")
        else:
            print(f"✗ Jalali to Gregorian conversion failed")
            return False
        
        # Test currency formatting
        formatted = format_currency(1000000)
        print(f"✓ Currency formatting works: {formatted}")
        
        # Test month names
        month_name = converter.get_jalali_month_name(1)
        print(f"✓ Persian month name works: {month_name}")
        
        return True
    except Exception as e:
        print(f"✗ Utility test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Iran Insurance Management Software - Installation Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Database Operations", test_database()))
    results.append(("Utility Functions", test_utilities()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! The software is ready to use.")
        print("\nTo run the application, execute:")
        print("    python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed:")
        print("    pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
