#!/usr/bin/env python3
"""
Installation and Setup Script for Iran Insurance Installment Management System
"""

import sys
import subprocess
import os

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print("Please install Python 3.8+ and try again.")
        return False
    
    print("✓ Python version is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    try:
        from src.models import init_database, get_session
        from src.controllers import AuthController
        
        print("Creating database tables...")
        init_database()
        print("✓ Database tables created")
        
        # Create default admin user
        session = get_session()
        auth = AuthController(session)
        
        from src.models import User
        user_count = session.query(User).count()
        
        if user_count == 0:
            print("\nCreating default admin user...")
            success, message, user = auth.register_user(
                username='admin',
                password='admin123',
                full_name='مدیر سیستم',
                email='admin@example.com',
                phone='09123456789',
                role='admin'
            )
            
            if success:
                print("✓ Default admin user created")
                print("  Username: admin")
                print("  Password: admin123")
                print("\n⚠️  IMPORTANT: Change the default password after first login!")
            else:
                print(f"❌ Error creating default user: {message}")
        else:
            print("✓ Database already has users")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print_header("Running Basic Tests")
    
    try:
        from src.models import get_session
        from src.controllers import AuthController
        
        session = get_session()
        auth = AuthController(session)
        
        # Test login
        print("Testing authentication...")
        success, message, user = auth.login('admin', 'admin123')
        if success:
            print("✓ Authentication test passed")
        else:
            print(f"❌ Authentication test failed: {message}")
            return False
        
        # Test Persian utilities
        print("Testing Persian utilities...")
        from src.utils.persian_utils import PersianDateConverter, format_currency
        from datetime import datetime
        
        persian_date = PersianDateConverter.gregorian_to_jalali(datetime.now())
        currency = format_currency(1000000)
        print(f"  Persian date: {persian_date}")
        print(f"  Currency format: {currency}")
        print("✓ Persian utilities test passed")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main setup function"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   Iran Insurance Installment Management System           ║
║   Setup and Installation Script                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    if not check_python_version():
        return 1
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return 1
    
    # Step 3: Initialize database
    if not initialize_database():
        return 1
    
    # Step 4: Run tests
    if not run_tests():
        return 1
    
    # Success message
    print_header("Setup Complete!")
    print("""
✓ Installation completed successfully!

To start the application, run:
    python main.py

Default Login Credentials:
    Username: admin
    Password: admin123

Features Available:
    • User authentication system
    • Insurance policy management
    • Installment tracking and calendar view
    • Advanced statistical charts
    • Custom report generation (Excel/CSV)
    • Smart reminders with desktop notifications
    • SMS reminder system (API configuration required)
    • Persian UI with RTL support
    • Solar Hijri calendar integration

For more information, see README.md

Enjoy using the Iran Insurance Installment Management System!
    """)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
