"""Database migration manager"""
import logging
import os
import sqlite3
from typing import List, Tuple

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db_path: str):
        """
        Initialize migration manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(50) UNIQUE NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        applied = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return applied
    
    def _mark_migration_applied(self, version: str):
        """Mark a migration as applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (version,)
        )
        
        conn.commit()
        conn.close()
    
    def _column_exists(self, cursor, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    def run_migrations(self):
        """Run all pending migrations"""
        logger.info("Starting database migrations...")
        
        applied = self._get_applied_migrations()
        logger.info(f"Already applied migrations: {applied}")
        
        # Define migrations in order
        migrations = [
            ('001_add_missing_columns', self._migration_001_add_missing_columns),
        ]
        
        for version, migration_func in migrations:
            if version not in applied:
                logger.info(f"Applying migration: {version}")
                try:
                    migration_func()
                    self._mark_migration_applied(version)
                    logger.info(f"Migration {version} applied successfully")
                except Exception as e:
                    logger.error(f"Migration {version} failed: {e}")
                    raise
            else:
                logger.debug(f"Migration {version} already applied, skipping")
        
        logger.info("All migrations completed")
    
    def _migration_001_add_missing_columns(self):
        """
        Migration 001: Add missing columns to tables
        
        Adds:
        - policies: mobile_number, down_payment, num_installments
        - users: is_active, last_login
        - installments: transaction_reference, is_reminder_sent, reminder_sent_date
        - reminders: user_id, title, message, scheduled_date, sent_date, 
                     recipient_phone, recipient_email, priority, is_recurring, 
                     recurrence_pattern
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Add missing columns to policies table
            if not self._column_exists(cursor, 'policies', 'mobile_number'):
                cursor.execute("ALTER TABLE policies ADD COLUMN mobile_number VARCHAR(20)")
                logger.info("Added mobile_number column to policies table")
            
            if not self._column_exists(cursor, 'policies', 'down_payment'):
                cursor.execute("ALTER TABLE policies ADD COLUMN down_payment FLOAT DEFAULT 0")
                logger.info("Added down_payment column to policies table")
            
            if not self._column_exists(cursor, 'policies', 'num_installments'):
                cursor.execute("ALTER TABLE policies ADD COLUMN num_installments INTEGER DEFAULT 0")
                logger.info("Added num_installments column to policies table")
            
            # Add missing columns to users table
            if not self._column_exists(cursor, 'users', 'is_active'):
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                logger.info("Added is_active column to users table")
            
            if not self._column_exists(cursor, 'users', 'last_login'):
                cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
                logger.info("Added last_login column to users table")
            
            # Add missing columns to installments table
            if not self._column_exists(cursor, 'installments', 'transaction_reference'):
                cursor.execute("ALTER TABLE installments ADD COLUMN transaction_reference VARCHAR(100)")
                logger.info("Added transaction_reference column to installments table")
            
            if not self._column_exists(cursor, 'installments', 'is_reminder_sent'):
                cursor.execute("ALTER TABLE installments ADD COLUMN is_reminder_sent BOOLEAN DEFAULT 0")
                logger.info("Added is_reminder_sent column to installments table")
            
            if not self._column_exists(cursor, 'installments', 'reminder_sent_date'):
                cursor.execute("ALTER TABLE installments ADD COLUMN reminder_sent_date DATETIME")
                logger.info("Added reminder_sent_date column to installments table")
            
            # Add missing columns to reminders table (if table exists)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
            if cursor.fetchone():
                if not self._column_exists(cursor, 'reminders', 'user_id'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN user_id INTEGER REFERENCES users(id)")
                    logger.info("Added user_id column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'title'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN title VARCHAR(200)")
                    logger.info("Added title column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'message'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN message TEXT")
                    logger.info("Added message column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'scheduled_date'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN scheduled_date DATETIME")
                    logger.info("Added scheduled_date column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'sent_date'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN sent_date DATETIME")
                    logger.info("Added sent_date column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'recipient_phone'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN recipient_phone VARCHAR(20)")
                    logger.info("Added recipient_phone column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'recipient_email'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN recipient_email VARCHAR(100)")
                    logger.info("Added recipient_email column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'priority'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN priority VARCHAR(20) DEFAULT 'normal'")
                    logger.info("Added priority column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'is_recurring'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN is_recurring BOOLEAN DEFAULT 0")
                    logger.info("Added is_recurring column to reminders table")
                
                if not self._column_exists(cursor, 'reminders', 'recurrence_pattern'):
                    cursor.execute("ALTER TABLE reminders ADD COLUMN recurrence_pattern VARCHAR(50)")
                    logger.info("Added recurrence_pattern column to reminders table")
            
            conn.commit()
            logger.info("Migration 001 completed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration 001 failed: {e}")
            raise
        finally:
            conn.close()
