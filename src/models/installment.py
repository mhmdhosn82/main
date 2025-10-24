"""Installment model for policy payments"""
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Installment(Base):
    """Installment payment model"""
    __tablename__ = 'installments'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    installment_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, paid, overdue, cancelled
    payment_method = Column(String(50))  # cash, card, transfer, etc.
    transaction_reference = Column(String(100))
    notes = Column(String(500))
    is_reminder_sent = Column(Boolean, default=False)
    reminder_sent_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    policy = relationship("InsurancePolicy", back_populates="installments")
    
    def __repr__(self):
        return f"<Installment(policy_id={self.policy_id}, number={self.installment_number}, status='{self.status}')>"
