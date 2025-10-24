#!/usr/bin/env python3
"""
Demo script showing programmatic usage of the Insurance Management System.
This demonstrates how to use the API without the GUI.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db import get_database
from src.models.models import InsurancePolicy
from src.models.repository import PolicyRepository, InstallmentRepository
from src.utils.helpers import generate_installments, get_current_jalali_date
from src.utils.export import export_policies_to_excel, export_installments_to_excel


def create_sample_data():
    """Create sample insurance policies and installments."""
    db = get_database()
    policy_repo = PolicyRepository(db)
    installment_repo = InstallmentRepository(db)
    
    print("Creating sample insurance policies...\n")
    
    # Sample policies
    sample_policies = [
        {
            'policy_number': 'INS-001-1402',
            'insured_name': 'علی احمدی',
            'issuance_date': '1402/03/15',
            'expiration_date': '1403/03/15',
            'advance_payment': 5000000,
            'total_installment_amount': 20000000,
            'number_of_installments': 12
        },
        {
            'policy_number': 'INS-002-1402',
            'insured_name': 'زهرا محمدی',
            'issuance_date': '1402/05/10',
            'expiration_date': '1403/05/10',
            'advance_payment': 3000000,
            'total_installment_amount': 15000000,
            'number_of_installments': 10
        },
        {
            'policy_number': 'INS-003-1402',
            'insured_name': 'حسن رضایی',
            'issuance_date': '1402/06/20',
            'expiration_date': '1403/06/20',
            'advance_payment': 7000000,
            'total_installment_amount': 30000000,
            'number_of_installments': 15
        }
    ]
    
    for policy_data in sample_policies:
        # Create policy
        policy = InsurancePolicy(**policy_data)
        policy_id = policy_repo.create_policy(policy)
        
        print(f"Created policy: {policy.policy_number} - {policy.insured_name}")
        print(f"  Policy ID: {policy_id}")
        print(f"  Issuance Date: {policy.issuance_date}")
        print(f"  Number of Installments: {policy.number_of_installments}")
        
        # Generate installments
        installments = generate_installments(
            policy_id,
            policy.issuance_date,
            policy.number_of_installments,
            policy.total_installment_amount
        )
        
        for inst in installments:
            installment_repo.create_installment(inst)
        
        print(f"  Generated {len(installments)} installments\n")
    
    db.close()
    print("Sample data created successfully!")


def display_statistics():
    """Display statistics about policies and installments."""
    db = get_database()
    policy_repo = PolicyRepository(db)
    
    stats = policy_repo.get_statistics()
    
    print("\n" + "="*60)
    print("Insurance Management Statistics")
    print("="*60)
    print(f"Total Policies: {stats['total_policies']}")
    print(f"Total Installments: {stats['total_installments']}")
    print(f"Paid Installments: {stats['paid_installments']}")
    print(f"Unpaid Installments: {stats['unpaid_installments']}")
    print("="*60 + "\n")
    
    db.close()


def list_all_policies():
    """List all insurance policies."""
    db = get_database()
    policy_repo = PolicyRepository(db)
    
    policies = policy_repo.get_all_policies()
    
    print("\n" + "="*60)
    print("All Insurance Policies")
    print("="*60)
    
    for policy in policies:
        print(f"\nPolicy Number: {policy.policy_number}")
        print(f"Insured Name: {policy.insured_name}")
        print(f"Issuance Date: {policy.issuance_date}")
        print(f"Expiration Date: {policy.expiration_date}")
        print(f"Advance Payment: {policy.advance_payment:,.0f} Rials")
        print(f"Total Installments: {policy.total_installment_amount:,.0f} Rials")
        print(f"Number of Installments: {policy.number_of_installments}")
        print("-" * 60)
    
    db.close()


def show_upcoming_installments():
    """Show upcoming installments."""
    db = get_database()
    installment_repo = InstallmentRepository(db)
    
    current_date = get_current_jalali_date()
    installments = installment_repo.get_due_installments()
    
    print("\n" + "="*60)
    print("Upcoming Unpaid Installments")
    print("="*60)
    
    for inst in installments[:10]:  # Show first 10
        print(f"\nPolicy: {inst['policy_number']} - {inst['insured_name']}")
        print(f"Installment #{inst['installment_number']}")
        print(f"Due Date: {inst['due_date']}")
        print(f"Amount: {inst['amount']:,.0f} Rials")
        print(f"Status: {inst['status']}")
        print("-" * 60)
    
    db.close()


def export_reports():
    """Export reports to Excel and PDF."""
    db = get_database()
    policy_repo = PolicyRepository(db)
    installment_repo = InstallmentRepository(db)
    
    print("\n" + "="*60)
    print("Exporting Reports")
    print("="*60)
    
    # Export policies
    policies = policy_repo.get_all_policies()
    policies_data = [p.to_dict() for p in policies]
    
    export_policies_to_excel(policies_data, 'policies_report.xlsx')
    print("✓ Exported policies to: policies_report.xlsx")
    
    # Export installments
    installments = installment_repo.get_due_installments()
    
    export_installments_to_excel(installments, 'installments_report.xlsx')
    print("✓ Exported installments to: installments_report.xlsx")
    
    print("="*60 + "\n")
    
    db.close()


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Iran Insurance Management System - Demo")
    print("="*60 + "\n")
    
    # Check if database has data
    db = get_database()
    policy_repo = PolicyRepository(db)
    stats = policy_repo.get_statistics()
    db.close()
    
    if stats['total_policies'] == 0:
        print("No data found. Creating sample data...")
        create_sample_data()
    
    # Display information
    display_statistics()
    list_all_policies()
    show_upcoming_installments()
    export_reports()
    
    print("\nDemo completed successfully!")
    print("\nTo run the GUI application, execute:")
    print("    python main.py")


if __name__ == "__main__":
    main()
