"""User model for authentication and management"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .database import Base
import bcrypt

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    role = Column(String(20), default='user')  # user, admin (for future multi-user)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f"<User(username='{self.username}', full_name='{self.full_name}')>"
