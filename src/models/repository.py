"""
Repository layer for database operations.
"""

from typing import List, Optional, Dict, Any
from src.models.models import InsurancePolicy, Installment
from src.database.db import Database
import jdatetime
from datetime import datetime


class PolicyRepository:
    """Repository for insurance policy operations."""
    
    def __init__(self, db: Database):
        """
        Initialize the repository.
        
        Args:
            db: Database instance
        """
        self.db = db
        
    def create_policy(self, policy: InsurancePolicy) -> int:
        """
        Create a new insurance policy.
        
        Args:
            policy: InsurancePolicy instance
            
        Returns:
            The ID of the created policy
        """
        self.db.cursor.execute("""
            INSERT INTO insurance_policies 
            (policy_number, insured_name, issuance_date, expiration_date,
             advance_payment, total_installment_amount, number_of_installments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            policy.policy_number,
            policy.insured_name,
            policy.issuance_date,
            policy.expiration_date,
            policy.advance_payment,
            policy.total_installment_amount,
            policy.number_of_installments
        ))
        self.db.connection.commit()
        return self.db.cursor.lastrowid
    
    def update_policy(self, policy: InsurancePolicy) -> bool:
        """
        Update an existing insurance policy.
        
        Args:
            policy: InsurancePolicy instance with id
            
        Returns:
            True if successful, False otherwise
        """
        if not policy.id:
            return False
            
        self.db.cursor.execute("""
            UPDATE insurance_policies
            SET policy_number = ?, insured_name = ?, issuance_date = ?,
                expiration_date = ?, advance_payment = ?,
                total_installment_amount = ?, number_of_installments = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            policy.policy_number,
            policy.insured_name,
            policy.issuance_date,
            policy.expiration_date,
            policy.advance_payment,
            policy.total_installment_amount,
            policy.number_of_installments,
            policy.id
        ))
        self.db.connection.commit()
        return True
    
    def get_policy_by_id(self, policy_id: int) -> Optional[InsurancePolicy]:
        """
        Get a policy by its ID.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            InsurancePolicy instance or None if not found
        """
        self.db.cursor.execute("""
            SELECT * FROM insurance_policies WHERE id = ?
        """, (policy_id,))
        row = self.db.cursor.fetchone()
        
        if row:
            return InsurancePolicy.from_dict(dict(row))
        return None
    
    def get_policy_by_number(self, policy_number: str) -> Optional[InsurancePolicy]:
        """
        Get a policy by its policy number.
        
        Args:
            policy_number: The policy number
            
        Returns:
            InsurancePolicy instance or None if not found
        """
        self.db.cursor.execute("""
            SELECT * FROM insurance_policies WHERE policy_number = ?
        """, (policy_number,))
        row = self.db.cursor.fetchone()
        
        if row:
            return InsurancePolicy.from_dict(dict(row))
        return None
    
    def get_all_policies(self, search_term: str = "") -> List[InsurancePolicy]:
        """
        Get all policies with optional search filter.
        
        Args:
            search_term: Optional search term to filter policies
            
        Returns:
            List of InsurancePolicy instances
        """
        if search_term:
            self.db.cursor.execute("""
                SELECT * FROM insurance_policies
                WHERE policy_number LIKE ? OR insured_name LIKE ?
                ORDER BY id DESC
            """, (f'%{search_term}%', f'%{search_term}%'))
        else:
            self.db.cursor.execute("""
                SELECT * FROM insurance_policies ORDER BY id DESC
            """)
        
        rows = self.db.cursor.fetchall()
        return [InsurancePolicy.from_dict(dict(row)) for row in rows]
    
    def delete_policy(self, policy_id: int) -> bool:
        """
        Delete a policy and its installments.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            True if successful, False otherwise
        """
        self.db.cursor.execute("""
            DELETE FROM insurance_policies WHERE id = ?
        """, (policy_id,))
        self.db.connection.commit()
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about policies.
        
        Returns:
            Dictionary with statistics
        """
        # Total policies
        self.db.cursor.execute("SELECT COUNT(*) as count FROM insurance_policies")
        total_policies = self.db.cursor.fetchone()['count']
        
        # Total installments
        self.db.cursor.execute("SELECT COUNT(*) as count FROM installments")
        total_installments = self.db.cursor.fetchone()['count']
        
        # Paid installments
        self.db.cursor.execute("SELECT COUNT(*) as count FROM installments WHERE status = 'paid'")
        paid_installments = self.db.cursor.fetchone()['count']
        
        # Unpaid installments
        unpaid_installments = total_installments - paid_installments
        
        return {
            'total_policies': total_policies,
            'total_installments': total_installments,
            'paid_installments': paid_installments,
            'unpaid_installments': unpaid_installments
        }


class InstallmentRepository:
    """Repository for installment operations."""
    
    def __init__(self, db: Database):
        """
        Initialize the repository.
        
        Args:
            db: Database instance
        """
        self.db = db
        
    def create_installment(self, installment: Installment) -> int:
        """
        Create a new installment.
        
        Args:
            installment: Installment instance
            
        Returns:
            The ID of the created installment
        """
        self.db.cursor.execute("""
            INSERT INTO installments
            (policy_id, installment_number, due_date, amount, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            installment.policy_id,
            installment.installment_number,
            installment.due_date,
            installment.amount,
            installment.status
        ))
        self.db.connection.commit()
        return self.db.cursor.lastrowid
    
    def update_installment_status(self, installment_id: int, status: str, paid_date: str = None) -> bool:
        """
        Update installment status.
        
        Args:
            installment_id: The installment ID
            status: New status ('paid' or 'unpaid')
            paid_date: Payment date (if paid)
            
        Returns:
            True if successful, False otherwise
        """
        self.db.cursor.execute("""
            UPDATE installments
            SET status = ?, paid_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, paid_date, installment_id))
        self.db.connection.commit()
        return True
    
    def get_installments_by_policy(self, policy_id: int) -> List[Installment]:
        """
        Get all installments for a specific policy.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            List of Installment instances
        """
        self.db.cursor.execute("""
            SELECT * FROM installments
            WHERE policy_id = ?
            ORDER BY installment_number
        """, (policy_id,))
        
        rows = self.db.cursor.fetchall()
        return [Installment.from_dict(dict(row)) for row in rows]
    
    def get_installment_by_id(self, installment_id: int) -> Optional[Installment]:
        """
        Get an installment by its ID.
        
        Args:
            installment_id: The installment ID
            
        Returns:
            Installment instance or None if not found
        """
        self.db.cursor.execute("""
            SELECT * FROM installments WHERE id = ?
        """, (installment_id,))
        row = self.db.cursor.fetchone()
        
        if row:
            return Installment.from_dict(dict(row))
        return None
    
    def get_due_installments(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get installments due within a date range with policy information.
        
        Args:
            start_date: Start date in Solar Hijri format (YYYY/MM/DD)
            end_date: End date in Solar Hijri format (YYYY/MM/DD)
            
        Returns:
            List of dictionaries with installment and policy information
        """
        if start_date and end_date:
            self.db.cursor.execute("""
                SELECT i.*, p.policy_number, p.insured_name
                FROM installments i
                JOIN insurance_policies p ON i.policy_id = p.id
                WHERE i.due_date BETWEEN ? AND ? AND i.status = 'unpaid'
                ORDER BY i.due_date
            """, (start_date, end_date))
        else:
            self.db.cursor.execute("""
                SELECT i.*, p.policy_number, p.insured_name
                FROM installments i
                JOIN insurance_policies p ON i.policy_id = p.id
                WHERE i.status = 'unpaid'
                ORDER BY i.due_date
            """)
        
        rows = self.db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def delete_installments_by_policy(self, policy_id: int) -> bool:
        """
        Delete all installments for a policy.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            True if successful, False otherwise
        """
        self.db.cursor.execute("""
            DELETE FROM installments WHERE policy_id = ?
        """, (policy_id,))
        self.db.connection.commit()
        return True
