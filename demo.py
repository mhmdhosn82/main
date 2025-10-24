#!/usr/bin/env python3
"""
Demo script showing programmatic usage of the Insurance Management System.
This demonstrates how to use the API without the GUI.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import init_database, get_session, User, InsurancePolicy, Installment
from src.controllers import AuthController, PolicyController, InstallmentController
from src.utils.persian_utils import PersianDateConverter, format_currency


def create_sample_data(session):
    """Create sample insurance policies and installments."""
    print("Creating sample insurance policies...\n")
    
    # Create a demo user if not exists
    auth_ctrl = AuthController(session)
    demo_user = session.query(User).filter_by(username='demo_user').first()
    
    if not demo_user:
        success, message, demo_user = auth_ctrl.register_user(
            username='demo_user',
            password='demo123',
            full_name='کاربر نمایشی',
            email='demo@example.com',
            phone='09123456789',
            role='user'
        )
        if not success:
            print(f"Error creating demo user: {message}")
            return
    
    policy_ctrl = PolicyController(session)
    installment_ctrl = InstallmentController(session)
    
    # Sample policies
    base_date = datetime.now()
    sample_policies = [
        {
            'policy_number': 'INS-001-1402',
            'policy_holder_name': 'علی احمدی',
            'policy_holder_national_id': '1234567890',
            'policy_type': 'Life',
            'insurance_company': 'بیمه ایران',
            'total_amount': 20000000,
            'start_date': base_date,
            'end_date': base_date + timedelta(days=365),
            'description': 'بیمه عمر'
        },
        {
            'policy_number': 'INS-002-1402',
            'policy_holder_name': 'زهرا محمدی',
            'policy_holder_national_id': '9876543210',
            'policy_type': 'Health',
            'insurance_company': 'بیمه ایران',
            'total_amount': 15000000,
            'start_date': base_date + timedelta(days=30),
            'end_date': base_date + timedelta(days=395),
            'description': 'بیمه درمان'
        },
        {
            'policy_number': 'INS-003-1402',
            'policy_holder_name': 'حسن رضایی',
            'policy_holder_national_id': '5555555555',
            'policy_type': 'Auto',
            'insurance_company': 'بیمه ایران',
            'total_amount': 30000000,
            'start_date': base_date + timedelta(days=60),
            'end_date': base_date + timedelta(days=425),
            'description': 'بیمه اتومبیل'
        }
    ]
    
    for policy_data in sample_policies:
        success, message, policy = policy_ctrl.create_policy(demo_user.id, policy_data)
        
        if success:
            print(f"Created policy: {policy.policy_number} - {policy.policy_holder_name}")
            print(f"  Policy ID: {policy.id}")
            converter = PersianDateConverter()
            jalali_date = converter.gregorian_to_jalali(policy.start_date)
            print(f"  Start Date: {jalali_date}")
            
            # Create sample installments
            num_installments = 12
            installment_amount = policy.total_amount / num_installments
            
            for i in range(num_installments):
                due_date = policy.start_date + timedelta(days=30 * (i + 1))
                installment = Installment(
                    policy_id=policy.id,
                    installment_number=i + 1,
                    amount=installment_amount,
                    due_date=due_date,
                    status='pending' if i > 0 else 'paid',
                    payment_date=policy.start_date if i == 0 else None
                )
                session.add(installment)
            
            session.commit()
            print(f"  Generated {num_installments} installments\n")
        else:
            print(f"Error creating policy: {message}\n")


def display_statistics(session):
    """Display statistics about policies and installments."""
    policy_ctrl = PolicyController(session)
    
    stats = policy_ctrl.get_policy_statistics()
    
    print("\n" + "="*60)
    print("Insurance Management Statistics")
    print("="*60)
    print(f"Total Policies: {stats.get('total_policies', 0)}")
    print(f"Active Policies: {stats.get('active_policies', 0)}")
    print(f"Total Amount: {format_currency(stats.get('total_amount', 0))}")
    print("="*60 + "\n")


def list_all_policies(session):
    """List all insurance policies."""
    policy_ctrl = PolicyController(session)
    
    policies = policy_ctrl.get_all_policies()
    
    print("\n" + "="*60)
    print("All Insurance Policies")
    print("="*60)
    
    converter = PersianDateConverter()
    for policy in policies:
        print(f"\nPolicy Number: {policy.policy_number}")
        print(f"Policy Holder: {policy.policy_holder_name}")
        print(f"Type: {policy.policy_type}")
        print(f"Company: {policy.insurance_company}")
        start_jalali = converter.gregorian_to_jalali(policy.start_date)
        end_jalali = converter.gregorian_to_jalali(policy.end_date)
        print(f"Start Date: {start_jalali}")
        print(f"End Date: {end_jalali}")
        print(f"Total Amount: {format_currency(policy.total_amount)}")
        print(f"Status: {policy.status}")
        print("-" * 60)


def show_upcoming_installments(session):
    """Show upcoming installments."""
    installment_ctrl = InstallmentController(session)
    
    # Get all pending installments
    all_installments = session.query(Installment).filter(
        Installment.status == 'pending'
    ).order_by(Installment.due_date).limit(10).all()
    
    print("\n" + "="*60)
    print("Upcoming Unpaid Installments")
    print("="*60)
    
    converter = PersianDateConverter()
    for inst in all_installments:
        policy = session.get(InsurancePolicy, inst.policy_id)
        print(f"\nPolicy: {policy.policy_number} - {policy.policy_holder_name}")
        print(f"Installment #{inst.installment_number}")
        due_jalali = converter.gregorian_to_jalali(inst.due_date)
        print(f"Due Date: {due_jalali}")
        print(f"Amount: {format_currency(inst.amount)}")
        print(f"Status: {inst.status}")
        print("-" * 60)


def export_reports(session):
    """Export reports to Excel."""
    from src.utils.export import export_to_excel
    
    print("\n" + "="*60)
    print("Exporting Reports")
    print("="*60)
    
    # Export policies
    policies = session.query(InsurancePolicy).all()
    converter = PersianDateConverter()
    
    policies_data = []
    for p in policies:
        policies_data.append({
            'شماره بیمه‌نامه': p.policy_number,
            'نام بیمه‌شده': p.policy_holder_name,
            'نوع بیمه': p.policy_type,
            'شرکت بیمه': p.insurance_company,
            'تاریخ شروع': converter.gregorian_to_jalali(p.start_date),
            'تاریخ پایان': converter.gregorian_to_jalali(p.end_date),
            'مبلغ کل': p.total_amount,
            'وضعیت': p.status
        })
    
    if policies_data:
        export_to_excel(policies_data, 'policies_report.xlsx', 'بیمه‌نامه‌ها')
        print("✓ Exported policies to: policies_report.xlsx")
    
    # Export installments
    installments = session.query(Installment).join(InsurancePolicy).all()
    installments_data = []
    
    for inst in installments:
        policy = session.get(InsurancePolicy, inst.policy_id)
        installments_data.append({
            'شماره بیمه‌نامه': policy.policy_number,
            'نام بیمه‌شده': policy.policy_holder_name,
            'شماره قسط': inst.installment_number,
            'تاریخ سررسید': converter.gregorian_to_jalali(inst.due_date),
            'مبلغ': inst.amount,
            'وضعیت': inst.status,
            'تاریخ پرداخت': converter.gregorian_to_jalali(inst.payment_date) if inst.payment_date else '-'
        })
    
    if installments_data:
        export_to_excel(installments_data, 'installments_report.xlsx', 'اقساط')
        print("✓ Exported installments to: installments_report.xlsx")
    
    print("="*60 + "\n")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Iran Insurance Management System - Demo")
    print("="*60 + "\n")
    
    # Initialize database
    init_database()
    session = get_session()
    
    try:
        # Check if database has data
        policy_ctrl = PolicyController(session)
        stats = policy_ctrl.get_policy_statistics()
        
        if stats['total_policies'] == 0:
            print("No data found. Creating sample data...")
            create_sample_data(session)
        
        # Display information
        display_statistics(session)
        list_all_policies(session)
        show_upcoming_installments(session)
        export_reports(session)
        
        print("\nDemo completed successfully!")
        print("\nTo run the GUI application, execute:")
        print("    python main.py")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
