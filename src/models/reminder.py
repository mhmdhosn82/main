"""Reminder model for notifications and SMS"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from datetime import datetime
from .database import Base

class Reminder(Base):
    """Reminder model for notifications"""
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    installment_id = Column(Integer, ForeignKey('installments.id'))
    reminder_type = Column(String(20))  # sms, notification, email
    title = Column(String(200))
    message = Column(Text)
    scheduled_date = Column(DateTime, nullable=False)
    sent_date = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed, cancelled
    recipient_phone = Column(String(20))
    recipient_email = Column(String(100))
    priority = Column(String(20), default='normal')  # low, normal, high
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Reminder(type='{self.reminder_type}', status='{self.status}')>"
