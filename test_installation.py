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
        from src.database.db import get_database
        from src.models.models import InsurancePolicy, Installment
        from src.models.repository import PolicyRepository, InstallmentRepository
        from src.utils.helpers import generate_installments, get_current_jalali_date
        from src.utils.export import export_policies_to_excel, export_policies_to_pdf
        print("✓ All core modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        print("✓ UI modules imported successfully")
    except ImportError as e:
        print(f"✗ UI import error: {e}")
        return False
    
    return True


def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    
    try:
        from src.database.db import get_database
        from src.models.models import InsurancePolicy
        from src.models.repository import PolicyRepository, InstallmentRepository
        from src.utils.helpers import generate_installments
        
        # Initialize database
        db = get_database()
        policy_repo = PolicyRepository(db)
        installment_repo = InstallmentRepository(db)
        
        # Create test policy
        policy = InsurancePolicy(
            policy_number='TEST-VERIFY',
            insured_name='تست نصب',
            issuance_date='1402/01/01',
            expiration_date='1403/01/01',
            advance_payment=1000000,
            total_installment_amount=10000000,
            number_of_installments=10
        )
        
        policy_id = policy_repo.create_policy(policy)
        print(f"✓ Policy created with ID: {policy_id}")
        
        # Generate installments
        installments = generate_installments(
            policy_id,
            policy.issuance_date,
            policy.number_of_installments,
            policy.total_installment_amount
        )
        
        for inst in installments:
            installment_repo.create_installment(inst)
        
        print(f"✓ Generated {len(installments)} installments")
        
        # Get statistics
        stats = policy_repo.get_statistics()
        print(f"✓ Statistics retrieved: {stats}")
        
        # Clean up
        policy_repo.delete_policy(policy_id)
        print("✓ Test policy cleaned up")
        
        # Close database
        db.close()
        
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
        from src.utils.helpers import (
            get_current_jalali_date,
            jalali_to_gregorian,
            gregorian_to_jalali,
            add_months_to_jalali_date
        )
        
        # Test date functions
        current = get_current_jalali_date()
        print(f"✓ Current Jalali date: {current}")
        
        greg = jalali_to_gregorian('1402/06/15')
        print(f"✓ Jalali to Gregorian conversion works")
        
        jalali = gregorian_to_jalali(greg)
        print(f"✓ Gregorian to Jalali conversion works")
        
        future = add_months_to_jalali_date('1402/01/01', 3)
        print(f"✓ Add months function works: {future}")
        
        return True
    except Exception as e:
        print(f"✗ Utility test error: {e}")
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
