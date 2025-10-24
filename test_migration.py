#!/usr/bin/env python3
"""
Test script to verify database migrations work correctly.
This test ensures that the migration system can handle:
1. Creating a fresh database with all columns
2. Migrating an old database to add missing columns
3. Running migrations multiple times (idempotent)
"""

import sys
import os
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cleanup_database():
    """Remove test database if it exists."""
    if os.path.exists('test_migration.db'):
        os.remove('test_migration.db')


def create_old_schema(db_path):
    """Create an old database schema missing the new columns."""
    print("Creating old database schema...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create old users table (missing is_active, last_login)
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            role VARCHAR(20),
            created_at DATETIME,
            updated_at DATETIME
        )
    """)
    
    # Create old policies table (missing mobile_number, down_payment, num_installments)
    cursor.execute("""
        CREATE TABLE policies (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            policy_number VARCHAR(50) UNIQUE NOT NULL,
            policy_holder_name VARCHAR(100) NOT NULL,
            policy_holder_national_id VARCHAR(20),
            policy_type VARCHAR(50),
            insurance_company VARCHAR(100),
            total_amount FLOAT NOT NULL,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            description VARCHAR(500),
            status VARCHAR(20),
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create old installments table (missing transaction_reference, is_reminder_sent, reminder_sent_date)
    cursor.execute("""
        CREATE TABLE installments (
            id INTEGER PRIMARY KEY,
            policy_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            amount FLOAT NOT NULL,
            due_date DATETIME NOT NULL,
            status VARCHAR(20),
            payment_date DATETIME,
            payment_method VARCHAR(50),
            notes VARCHAR(500),
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (policy_id) REFERENCES policies(id)
        )
    """)
    
    # Create old reminders table (missing many columns)
    cursor.execute("""
        CREATE TABLE reminders (
            id INTEGER PRIMARY KEY,
            policy_id INTEGER,
            installment_id INTEGER,
            reminder_date DATETIME NOT NULL,
            reminder_type VARCHAR(50),
            status VARCHAR(20),
            sent_at DATETIME,
            notes VARCHAR(500),
            created_at DATETIME,
            FOREIGN KEY (policy_id) REFERENCES policies(id),
            FOREIGN KEY (installment_id) REFERENCES installments(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Old schema created")


def verify_columns(db_path, table_name, expected_columns):
    """Verify that all expected columns exist in the table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    actual_columns = {row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    missing_columns = set(expected_columns) - actual_columns
    
    if missing_columns:
        print(f"✗ Missing columns in {table_name}: {missing_columns}")
        return False
    else:
        print(f"✓ All expected columns exist in {table_name}")
        return True


def test_fresh_database_migration():
    """Test migration on a fresh database."""
    print("\n" + "=" * 60)
    print("Test 1: Fresh Database Migration")
    print("=" * 60)
    
    cleanup_database()
    
    try:
        from src.models.database import Base
        from sqlalchemy import create_engine
        from src.migrations import MigrationManager
        
        # Create database with SQLAlchemy
        db_path = 'test_migration.db'
        engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Import all models to register them
        from src.models import user, policy, installment, reminder
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Run migrations
        migration_manager = MigrationManager(db_path)
        migration_manager.run_migrations()
        
        # Verify all columns exist
        policies_columns = ['id', 'user_id', 'policy_number', 'policy_holder_name', 
                           'mobile_number', 'down_payment', 'num_installments']
        
        users_columns = ['id', 'username', 'is_active', 'last_login']
        
        installments_columns = ['id', 'policy_id', 'transaction_reference', 
                               'is_reminder_sent', 'reminder_sent_date']
        
        success = True
        success &= verify_columns(db_path, 'policies', policies_columns)
        success &= verify_columns(db_path, 'users', users_columns)
        success &= verify_columns(db_path, 'installments', installments_columns)
        
        cleanup_database()
        
        return success
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_database()
        return False


def test_old_database_migration():
    """Test migration on an old database schema."""
    print("\n" + "=" * 60)
    print("Test 2: Old Database Migration")
    print("=" * 60)
    
    cleanup_database()
    
    try:
        db_path = 'test_migration.db'
        
        # Create old schema
        create_old_schema(db_path)
        
        # Run migrations
        from src.migrations import MigrationManager
        migration_manager = MigrationManager(db_path)
        migration_manager.run_migrations()
        
        # Verify all new columns were added
        policies_columns = ['mobile_number', 'down_payment', 'num_installments']
        users_columns = ['is_active', 'last_login']
        installments_columns = ['transaction_reference', 'is_reminder_sent', 'reminder_sent_date']
        reminders_columns = ['user_id', 'title', 'message', 'scheduled_date', 'sent_date']
        
        success = True
        success &= verify_columns(db_path, 'policies', policies_columns)
        success &= verify_columns(db_path, 'users', users_columns)
        success &= verify_columns(db_path, 'installments', installments_columns)
        success &= verify_columns(db_path, 'reminders', reminders_columns)
        
        cleanup_database()
        
        return success
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_database()
        return False


def test_idempotent_migrations():
    """Test that running migrations multiple times doesn't cause errors."""
    print("\n" + "=" * 60)
    print("Test 3: Idempotent Migrations")
    print("=" * 60)
    
    cleanup_database()
    
    try:
        db_path = 'test_migration.db'
        
        # Create old schema
        create_old_schema(db_path)
        
        # Run migrations multiple times
        from src.migrations import MigrationManager
        
        for i in range(3):
            print(f"Running migration #{i+1}...")
            migration_manager = MigrationManager(db_path)
            migration_manager.run_migrations()
        
        print("✓ Migrations ran successfully 3 times without errors")
        
        # Verify columns still exist
        policies_columns = ['mobile_number', 'down_payment', 'num_installments']
        success = verify_columns(db_path, 'policies', policies_columns)
        
        cleanup_database()
        
        return success
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_database()
        return False


def test_create_policy_with_new_fields():
    """Test creating a policy with new fields after migration."""
    print("\n" + "=" * 60)
    print("Test 4: Create Policy with New Fields")
    print("=" * 60)
    
    cleanup_database()
    
    try:
        # Use test database
        db_path = 'test_migration.db'
        original_db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'insurance.db'
        )
        
        # Temporarily override DB_PATH
        from src.models import database
        database.DB_PATH = db_path
        
        # Create old schema
        create_old_schema(db_path)
        
        # Initialize database with migrations
        from src.models import init_database, get_session, User
        from src.controllers import AuthController, PolicyController
        from datetime import datetime, timedelta
        
        init_database()
        session = get_session()
        
        # Create test user
        auth_ctrl = AuthController(session)
        success, message, test_user = auth_ctrl.register_user(
            username='test_migration_user',
            password='test123',
            full_name='Test User',
            email='test@migration.com',
            phone='09123456789',
            role='user'
        )
        
        if not success:
            print(f"✗ Failed to create user: {message}")
            session.close()
            database.DB_PATH = original_db_path
            cleanup_database()
            return False
        
        # Create policy with new fields
        policy_ctrl = PolicyController(session)
        
        base_date = datetime.now()
        policy_data = {
            'policy_number': 'MIG-TEST-001',
            'policy_holder_name': 'Migration Test',
            'policy_holder_national_id': '1234567890',
            'mobile_number': '09123456789',  # NEW FIELD
            'policy_type': 'Life',
            'insurance_company': 'Test Insurance',
            'total_amount': 30000000,
            'down_payment': 10000000,  # NEW FIELD
            'num_installments': 10,  # NEW FIELD
            'start_date': base_date,
            'end_date': base_date + timedelta(days=365),
            'description': 'Migration test policy'
        }
        
        success, message, policy = policy_ctrl.create_policy(test_user.id, policy_data)
        
        if not success:
            print(f"✗ Failed to create policy: {message}")
            session.close()
            database.DB_PATH = original_db_path
            cleanup_database()
            return False
        
        # Verify new fields
        if (policy.mobile_number == '09123456789' and
            policy.down_payment == 10000000 and
            policy.num_installments == 10):
            print("✓ Policy created successfully with new fields:")
            print(f"  - Mobile Number: {policy.mobile_number}")
            print(f"  - Down Payment: {policy.down_payment}")
            print(f"  - Number of Installments: {policy.num_installments}")
            session.close()
            database.DB_PATH = original_db_path
            cleanup_database()
            return True
        else:
            print("✗ Policy fields don't match expected values")
            session.close()
            database.DB_PATH = original_db_path
            cleanup_database()
            return False
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        # Restore original DB_PATH
        from src.models import database
        database.DB_PATH = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'insurance.db'
        )
        cleanup_database()
        return False


def main():
    """Run all migration tests."""
    print("=" * 60)
    print("Database Migration Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Fresh Database Migration", test_fresh_database_migration()))
    results.append(("Old Database Migration", test_old_database_migration()))
    results.append(("Idempotent Migrations", test_idempotent_migrations()))
    results.append(("Create Policy with New Fields", test_create_policy_with_new_fields()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All migration tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
