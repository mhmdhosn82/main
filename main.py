"""Main application entry point"""
import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from src.models import init_database, get_session, User
from src.controllers import AuthController
from src.ui import LoginDialog, MainWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('insurance_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_default_user_if_needed(session):
    """Create default admin user if no users exist"""
    auth_ctrl = AuthController(session)
    
    # Check if any users exist
    user_count = session.query(User).count()
    
    if user_count == 0:
        logger.info("No users found, creating default admin user")
        success, message, user = auth_ctrl.register_user(
            username='admin',
            password='admin123',
            full_name='مدیر سیستم',
            email='admin@example.com',
            phone='09123456789',
            role='admin'
        )
        
        if success:
            logger.info("Default admin user created successfully")
            return True
        else:
            logger.error(f"Failed to create default user: {message}")
            return False
    
    return True

def main():
    """Main application function"""
    try:
        # Initialize Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("Iran Insurance Installment Manager")
        app.setLayoutDirection(Qt.RightToLeft)
        
        # Set application style
        app.setStyle('Fusion')
        
        logger.info("Starting Iran Insurance Installment Management System")
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Get database session
        session = get_session()
        
        # Create default user if needed
        if not create_default_user_if_needed(session):
            QMessageBox.critical(
                None,
                "خطا",
                "خطا در ایجاد کاربر پیش‌فرض. لطفاً لاگ‌ها را بررسی کنید."
            )
            return 1
        
        # Create and show login dialog
        auth_controller = AuthController(session)
        login_dialog = LoginDialog(auth_controller)
        
        # Show login dialog
        if login_dialog.exec_() == LoginDialog.Accepted:
            user = auth_controller.get_current_user()
            
            if user:
                logger.info(f"User '{user.username}' logged in successfully")
                
                # Create and show main window
                main_window = MainWindow(user, session)
                main_window.show()
                
                # Run application
                exit_code = app.exec_()
                
                # Cleanup
                logger.info("Application closing")
                session.close()
                
                return exit_code
            else:
                logger.error("Login succeeded but user object is None")
                return 1
        else:
            logger.info("User cancelled login")
            session.close()
            return 0
    
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        QMessageBox.critical(
            None,
            "خطای جدی",
            f"خطای غیرمنتظره:\n{str(e)}\n\nلطفاً لاگ‌ها را بررسی کنید."
        )
        return 1

if __name__ == '__main__':
    sys.exit(main())
