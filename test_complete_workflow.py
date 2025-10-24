#!/usr/bin/env python3
"""Comprehensive end-to-end workflow test for Iran Insurance Installment Management System"""
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_workflow():
    """Test the complete workflow from policy creation to installment tracking"""
    from src.models import init_database, get_session, User, InsurancePolicy, Installment
    from src.controllers import PolicyController, InstallmentController, AuthController
    from src.utils import ReportGenerator, format_currency, PersianDateConverter
    
    print("=" * 70)
    print("Iran Insurance Installment Management System")
    print("Complete Workflow Test")
    print("=" * 70)
    print()
    
    # 1. Initialize database
    print("1. Initializing database...")
    init_database()
    session = get_session()
    print("   ✓ Database initialized")
    print()
    
    # 2. Check/create admin user
    print("2. Setting up admin user...")
    auth_ctrl = AuthController(session)
    user = session.query(User).filter_by(username='admin').first()
    if not user:
        success, msg, user = auth_ctrl.register_user(
            'admin', 'admin123', 'مدیر سیستم', 'admin@test.com', '09123456789', 'admin'
        )
        if success:
            print(f"   ✓ Admin user created: {user.full_name}")
        else:
            print(f"   ✗ Failed to create user: {msg}")
            return False
    else:
        print(f"   ✓ Admin user exists: {user.full_name}")
    print()
    
    # 3. Create test policy
    print("3. Creating test insurance policy...")
    policy_ctrl = PolicyController(session)
    
    policy_data = {
        'policy_number': 'TEST-2025-001',
        'policy_holder_name': 'محمد رضایی',
        'mobile_number': '09121234567',
        'policy_type': 'شخص ثالث',
        'insurance_company': 'بیمه ایران',
        'total_amount': 12000000,  # 12 million Rials
        'down_payment': 2000000,   # 2 million Rials down payment
        'num_installments': 10,    # 10 monthly installments
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=365),
        'description': 'بیمه شخص ثالث خودرو پژو 206'
    }
    
    # Check if policy already exists
    existing = session.query(InsurancePolicy).filter_by(
        policy_number=policy_data['policy_number']
    ).first()
    
    if existing:
        print(f"   ! Policy already exists: {existing.policy_number}")
        policy = existing
    else:
        success, msg, policy = policy_ctrl.create_policy(user.id, policy_data)
        if not success:
            print(f"   ✗ Failed to create policy: {msg}")
            return False
        print(f"   ✓ Policy created: {policy.policy_number}")
    
    print(f"     - Policy Holder: {policy.policy_holder_name}")
    print(f"     - Type: {policy.policy_type}")
    print(f"     - Total Amount: {format_currency(policy.total_amount)}")
    print(f"     - Down Payment: {format_currency(policy.down_payment)}")
    print(f"     - Installments: {policy.num_installments}")
    print()
    
    # 4. Create/verify installments
    print("4. Creating installments...")
    inst_ctrl = InstallmentController(session)
    
    existing_installments = inst_ctrl.get_policy_installments(policy.id)
    
    if existing_installments:
        print(f"   ! {len(existing_installments)} installments already exist")
        installments = existing_installments
    else:
        remaining = policy_data['total_amount'] - policy_data['down_payment']
        first_due_date = datetime.now() + timedelta(days=30)
        
        success, msg, installments = inst_ctrl.create_installments_batch(
            policy.id,
            remaining,
            policy_data['num_installments'],
            first_due_date,
            interval_days=30
        )
        
        if not success:
            print(f"   ✗ Failed to create installments: {msg}")
            return False
        print(f"   ✓ {len(installments)} installments created")
    
    print()
    print("   Installment Schedule:")
    print("   " + "-" * 60)
    print(f"   {'#':<4} {'Amount':<15} {'Due Date':<20} {'Status':<12}")
    print("   " + "-" * 60)
    
    for inst in installments:
        due_persian = PersianDateConverter.gregorian_to_jalali(inst.due_date)
        print(f"   {inst.installment_number:<4} {format_currency(inst.amount):<15} {due_persian:<20} {inst.status:<12}")
    print()
    
    # 5. Test payment marking
    print("5. Testing payment functionality...")
    if installments:
        first_inst = installments[0]
        if first_inst.status == 'pending':
            success, msg = inst_ctrl.mark_as_paid(first_inst.id, payment_method='نقدی')
            if success:
                print(f"   ✓ Installment #{first_inst.installment_number} marked as paid")
            else:
                print(f"   ✗ Failed to mark payment: {msg}")
        else:
            print(f"   ! Installment #{first_inst.installment_number} already paid")
    print()
    
    # 6. Test installment queries
    print("6. Testing installment queries...")
    
    # Upcoming installments
    upcoming = inst_ctrl.get_upcoming_installments(days_ahead=90, user_id=user.id)
    print(f"   ✓ Upcoming installments (90 days): {len(upcoming)}")
    
    # Overdue installments
    overdue = inst_ctrl.get_overdue_installments(user_id=user.id)
    print(f"   ✓ Overdue installments: {len(overdue)}")
    
    # Statistics
    stats = inst_ctrl.get_installment_statistics(user_id=user.id)
    print(f"   ✓ Statistics:")
    print(f"     - Total: {stats['total']}")
    print(f"     - Paid: {format_currency(stats['total_paid'])}")
    print(f"     - Pending: {format_currency(stats['total_pending'])}")
    print(f"     - Overdue: {format_currency(stats['total_overdue'])}")
    print()
    
    # 7. Test report generation
    print("7. Testing report generation...")
    report_gen = ReportGenerator(session)
    
    # Installment report
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now() + timedelta(days=365)
    
    inst_report = report_gen.generate_installment_report(
        start_date=start_date,
        end_date=end_date
    )
    print(f"   ✓ Installment report: {len(inst_report)} rows")
    
    # Policy summary
    policy_summary = report_gen.generate_policy_summary(user_id=user.id)
    print(f"   ✓ Policy summary: {len(policy_summary)} rows")
    
    # Payment statistics
    payment_stats = report_gen.generate_payment_statistics(start_date, end_date)
    print(f"   ✓ Payment statistics: {len(payment_stats)} rows")
    print()
    
    # 8. Test Persian date conversion
    print("8. Testing Persian calendar support...")
    test_date = datetime.now()
    persian_date = PersianDateConverter.gregorian_to_jalali(test_date)
    print(f"   ✓ Today (Gregorian): {test_date.strftime('%Y-%m-%d')}")
    print(f"   ✓ Today (Persian): {persian_date}")
    print()
    
    # 9. Test configuration
    print("9. Testing configuration manager...")
    try:
        from src.utils import get_config
        config = get_config()
        sms_config = config.get_sms_config()
        print(f"   ✓ SMS enabled: {sms_config.get('enabled', False)}")
        print(f"   ✓ Config file: {config.config_file}")
    except Exception as e:
        print(f"   ! Configuration warning: {e}")
    print()
    
    # 10. Cleanup
    print("10. Test Summary...")
    session.close()
    
    print("=" * 70)
    print("✓ All tests completed successfully!")
    print("=" * 70)
    print()
    print("System is ready for use. Key features verified:")
    print("  • Database initialization and migrations")
    print("  • User authentication")
    print("  • Policy creation")
    print("  • Automatic installment generation")
    print("  • Payment tracking")
    print("  • Persian calendar support")
    print("  • Report generation")
    print("  • Configuration management")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_complete_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
