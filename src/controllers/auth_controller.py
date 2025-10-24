"""Authentication controller"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthController:
    """Handle user authentication"""
    
    def __init__(self, session):
        self.session = session
        self.current_user = None
    
    def login(self, username, password):
        """
        Authenticate user with username and password
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        from ..models import User
        
        try:
            user = self.session.query(User).filter(
                User.username == username
            ).first()
            
            if not user:
                logger.warning(f"Login failed: User '{username}' not found")
                return False, "نام کاربری یا رمز عبور اشتباه است", None
            
            if not user.is_active:
                logger.warning(f"Login failed: User '{username}' is inactive")
                return False, "حساب کاربری غیرفعال است", None
            
            if not user.check_password(password):
                logger.warning(f"Login failed: Invalid password for '{username}'")
                return False, "نام کاربری یا رمز عبور اشتباه است", None
            
            # Update last login
            user.last_login = datetime.now()
            self.session.commit()
            
            self.current_user = user
            logger.info(f"User '{username}' logged in successfully")
            return True, "ورود موفقیت‌آمیز بود", user
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.session.rollback()
            return False, "خطا در ورود به سیستم", None
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            logger.info(f"User '{self.current_user.username}' logged out")
        self.current_user = None
    
    def register_user(self, username, password, full_name, email=None, phone=None, role='user'):
        """
        Register a new user
        
        Args:
            username: Username
            password: Password
            full_name: Full name
            email: Email address (optional)
            phone: Phone number (optional)
            role: User role (default: 'user')
            
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        from ..models import User
        
        try:
            # Check if username already exists
            existing = self.session.query(User).filter(
                User.username == username
            ).first()
            
            if existing:
                return False, "نام کاربری قبلاً استفاده شده است", None
            
            # Create new user
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                phone=phone,
                role=role
            )
            user.set_password(password)
            
            self.session.add(user)
            self.session.commit()
            
            logger.info(f"New user registered: '{username}'")
            return True, "ثبت‌نام با موفقیت انجام شد", user
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            self.session.rollback()
            return False, f"خطا در ثبت‌نام: {str(e)}", None
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        from ..models import User
        
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "کاربر یافت نشد"
            
            if not user.check_password(old_password):
                return False, "رمز عبور فعلی اشتباه است"
            
            user.set_password(new_password)
            self.session.commit()
            
            logger.info(f"Password changed for user '{user.username}'")
            return True, "رمز عبور با موفقیت تغییر کرد"
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            self.session.rollback()
            return False, f"خطا در تغییر رمز عبور: {str(e)}"
    
    def get_current_user(self):
        """Get currently logged in user"""
        return self.current_user
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.current_user is not None
