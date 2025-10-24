"""Insurance policy model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class InsurancePolicy(Base):
    """Insurance policy model"""
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    policy_number = Column(String(50), unique=True, nullable=False)
    policy_holder_name = Column(String(100), nullable=False)
    policy_holder_national_id = Column(String(20))
    policy_type = Column(String(50))  # Life, Health, Auto, Property, etc.
    insurance_company = Column(String(100))
    total_amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    description = Column(String(500))
    status = Column(String(20), default='active')  # active, expired, cancelled
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    installments = relationship("Installment", back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Policy(number='{self.policy_number}', holder='{self.policy_holder_name}')>"
