"""Test script to verify all the new features"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base
from src.models.user import User
from src.models.policy import InsurancePolicy
from src.models.installment import Installment
from src.controllers.policy_controller import PolicyController
from src.controllers.installment_controller import InstallmentController
from src.utils.report_generator import ReportGenerator
import bcrypt

def test_features():
    """Test all new features"""
    
    # Create in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create test user
    password = "test123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username="testuser",
        password_hash=hashed.decode('utf-8'),
        full_name="Test User",
        email="test@test.com"
    )
    session.add(user)
    session.commit()
    
    print("✓ Test 1: User created")
    
    # Test 2: Create policy with "مسئولیت" type
    policy_controller = PolicyController(session)
    policy_data = {
        'policy_number': 'TEST-001',
        'policy_holder_name': 'تست بیمه‌گذار',
        'mobile_number': '09123456789',
        'policy_type': 'مسئولیت',  # New policy type
        'insurance_company': 'شرکت بیمه ایران',
        'total_amount': 10000000,
        'down_payment': 2000000,
        'num_installments': 4,
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=365),
        'description': 'تست بیمه‌نامه مسئولیت'
    }
    
    success, message, policy = policy_controller.create_policy(user.id, policy_data)
    assert success, f"Failed to create policy: {message}"
    assert policy.policy_type == 'مسئولیت', "Policy type should be 'مسئولیت'"
    print("✓ Test 2: Policy with 'مسئولیت' type created successfully")
    
    # Test 3: Create installments
    installment_controller = InstallmentController(session)
    remaining = policy_data['total_amount'] - policy_data['down_payment']
    first_date = datetime.now() + timedelta(days=30)
    
    success, message, installments = installment_controller.create_installments_batch(
        policy.id, remaining, 4, first_date, 30
    )
    assert success, f"Failed to create installments: {message}"
    assert len(installments) == 4, "Should create 4 installments"
    print("✓ Test 3: Installments created successfully")
    
    # Test 4: Create overdue installment (>1 month past due)
    overdue_date = datetime.now() - timedelta(days=45)
    overdue_installment = Installment(
        policy_id=policy.id,
        installment_number=5,
        amount=500000,
        due_date=overdue_date,
        status='pending'
    )
    session.add(overdue_installment)
    session.commit()
    
    # Query overdue installments
    one_month_ago = datetime.now() - timedelta(days=30)
    overdue = session.query(Installment).filter(
        Installment.due_date < one_month_ago,
        Installment.status.in_(['pending', 'overdue'])
    ).all()
    assert len(overdue) >= 1, "Should have at least one overdue installment"
    print("✓ Test 4: Overdue installment detection works")
    
    # Test 5: Mark all installments as paid and verify auto-delete
    policy2_data = {
        'policy_number': 'TEST-002',
        'policy_holder_name': 'تست بیمه‌گذار 2',
        'mobile_number': '09123456790',
        'policy_type': 'شخص ثالث',
        'insurance_company': 'شرکت بیمه ایران',
        'total_amount': 5000000,
        'down_payment': 1000000,
        'num_installments': 2,
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=180),
        'description': 'تست اتو-دیلیت'
    }
    
    success, message, policy2 = policy_controller.create_policy(user.id, policy2_data)
    assert success, f"Failed to create policy2: {message}"
    
    success, message, installments2 = installment_controller.create_installments_batch(
        policy2.id, 4000000, 2, datetime.now() + timedelta(days=30), 30
    )
    assert success, f"Failed to create installments for policy2: {message}"
    
    # Mark all installments as paid
    for inst in installments2:
        success, message = installment_controller.mark_as_paid(inst.id)
        assert success, f"Failed to mark installment as paid: {message}"
    
    # Verify policy is auto-deleted
    deleted_policy = policy_controller.get_policy(policy2.id)
    assert deleted_policy is None, "Policy should be auto-deleted after all installments paid"
    print("✓ Test 5: Auto-delete policy when all installments paid works")
    
    # Test 6: Manual delete policy
    policies_before = len(policy_controller.get_all_policies(user.id))
    success, message = policy_controller.delete_policy(policy.id)
    assert success, f"Failed to delete policy: {message}"
    policies_after = len(policy_controller.get_all_policies(user.id))
    assert policies_after == policies_before - 1, "Policy count should decrease by 1"
    print("✓ Test 6: Manual policy deletion works")
    
    # Test 7: Excel export with Persian headers
    # Create a new policy for export test
    policy3_data = {
        'policy_number': 'TEST-003',
        'policy_holder_name': 'تست بیمه‌گذار 3',
        'mobile_number': '09123456791',
        'policy_type': 'بدنه',
        'insurance_company': 'شرکت بیمه ایران',
        'total_amount': 8000000,
        'down_payment': 1500000,
        'num_installments': 3,
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=270),
        'description': 'تست اکسپورت'
    }
    
    success, message, policy3 = policy_controller.create_policy(user.id, policy3_data)
    assert success, f"Failed to create policy3: {message}"
    
    success, message, installments3 = installment_controller.create_installments_batch(
        policy3.id, 6500000, 3, datetime.now() + timedelta(days=30), 30
    )
    
    # Generate report
    report_gen = ReportGenerator(session)
    df = report_gen.generate_installment_report()
    
    # Check Persian headers
    persian_headers = ['شماره بیمه‌نامه', 'نام بیمه‌گذار', 'نوع بیمه', 'شماره قسط', 
                      'مبلغ', 'تاریخ سررسید', 'تاریخ پرداخت', 'وضعیت', 'روش پرداخت']
    for header in persian_headers:
        assert header in df.columns, f"Persian header '{header}' should be in DataFrame columns"
    print("✓ Test 7: Excel export with Persian headers works")
    
    # Test 8: Policy summary report with Persian headers
    df_summary = report_gen.generate_policy_summary(user.id)
    summary_headers = ['شماره بیمه‌نامه', 'نام بیمه‌گذار', 'نوع بیمه', 'مبلغ کل', 
                      'تعداد اقساط', 'مجموع پرداخت شده', 'مجموع باقی‌مانده', 'وضعیت']
    for header in summary_headers:
        assert header in df_summary.columns, f"Persian header '{header}' should be in summary DataFrame columns"
    print("✓ Test 8: Policy summary report with Persian headers works")
    
    session.close()
    print("\n✅ All tests passed successfully!")

if __name__ == "__main__":
    try:
        test_features()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
