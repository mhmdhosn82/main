"""
Data models for the Insurance Management System.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import jdatetime


@dataclass
class InsurancePolicy:
    """Model representing an insurance policy."""
    
    policy_number: str
    insured_name: str
    issuance_date: str  # Solar Hijri format: YYYY/MM/DD
    expiration_date: str  # Solar Hijri format: YYYY/MM/DD
    advance_payment: float
    total_installment_amount: float
    number_of_installments: int
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the policy to a dictionary."""
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'insured_name': self.insured_name,
            'issuance_date': self.issuance_date,
            'expiration_date': self.expiration_date,
            'advance_payment': self.advance_payment,
            'total_installment_amount': self.total_installment_amount,
            'number_of_installments': self.number_of_installments,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InsurancePolicy':
        """Create an InsurancePolicy instance from a dictionary."""
        return cls(
            id=data.get('id'),
            policy_number=data['policy_number'],
            insured_name=data['insured_name'],
            issuance_date=data['issuance_date'],
            expiration_date=data['expiration_date'],
            advance_payment=data['advance_payment'],
            total_installment_amount=data['total_installment_amount'],
            number_of_installments=data['number_of_installments'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


@dataclass
class Installment:
    """Model representing an installment."""
    
    policy_id: int
    installment_number: int
    due_date: str  # Solar Hijri format: YYYY/MM/DD
    amount: float
    status: str = 'unpaid'  # 'paid' or 'unpaid'
    id: Optional[int] = None
    paid_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the installment to a dictionary."""
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'installment_number': self.installment_number,
            'due_date': self.due_date,
            'amount': self.amount,
            'status': self.status,
            'paid_date': self.paid_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Installment':
        """Create an Installment instance from a dictionary."""
        return cls(
            id=data.get('id'),
            policy_id=data['policy_id'],
            installment_number=data['installment_number'],
            due_date=data['due_date'],
            amount=data['amount'],
            status=data.get('status', 'unpaid'),
            paid_date=data.get('paid_date'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
