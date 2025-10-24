# Database Migration System

This directory contains the database migration system for the Iran Insurance Management System.

## Overview

The migration system automatically updates the database schema when the application starts, ensuring that existing databases are updated to match the current model definitions without data loss.

## Features

- **Automatic Migration**: Migrations run automatically when `init_database()` is called
- **Idempotent**: Migrations can be run multiple times safely without errors
- **Tracked**: Applied migrations are tracked in the `schema_migrations` table
- **Non-destructive**: Only adds missing columns, never removes data

## Migration Files

### `migration_manager.py`
The core migration manager that:
- Creates and manages the `schema_migrations` tracking table
- Runs pending migrations in order
- Checks for existing columns before adding them
- Logs all migration activities

## Current Migrations

### Migration 001: Add Missing Columns
**Version**: `001_add_missing_columns`

Adds the following columns to existing tables:

#### Policies Table
- `mobile_number` (VARCHAR(20)) - Mobile number for SMS reminders
- `down_payment` (FLOAT) - Down payment amount
- `num_installments` (INTEGER) - Number of installments

#### Users Table
- `is_active` (BOOLEAN) - User active status
- `last_login` (DATETIME) - Last login timestamp

#### Installments Table
- `transaction_reference` (VARCHAR(100)) - Payment transaction reference
- `is_reminder_sent` (BOOLEAN) - Whether reminder was sent
- `reminder_sent_date` (DATETIME) - When reminder was sent

#### Reminders Table
- `user_id` (INTEGER) - Foreign key to users table
- `title` (VARCHAR(200)) - Reminder title
- `message` (TEXT) - Reminder message
- `scheduled_date` (DATETIME) - When to send reminder
- `sent_date` (DATETIME) - When reminder was sent
- `recipient_phone` (VARCHAR(20)) - Recipient phone number
- `recipient_email` (VARCHAR(100)) - Recipient email
- `priority` (VARCHAR(20)) - Reminder priority (low/normal/high)
- `is_recurring` (BOOLEAN) - Whether reminder recurs
- `recurrence_pattern` (VARCHAR(50)) - Recurrence pattern

## Adding New Migrations

To add a new migration:

1. Create a new migration method in `migration_manager.py`:
```python
def _migration_002_your_migration_name(self):
    """
    Migration 002: Description of what this migration does
    """
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        # Your migration code here
        if not self._column_exists(cursor, 'table_name', 'column_name'):
            cursor.execute("ALTER TABLE table_name ADD COLUMN column_name TYPE")
            logger.info("Added column_name column to table_name")
        
        conn.commit()
        logger.info("Migration 002 completed successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration 002 failed: {e}")
        raise
    finally:
        conn.close()
```

2. Add the migration to the `run_migrations()` method:
```python
migrations = [
    ('001_add_missing_columns', self._migration_001_add_missing_columns),
    ('002_your_migration_name', self._migration_002_your_migration_name),
]
```

## Testing

Run the migration tests to verify everything works:

```bash
python test_migration.py
```

This will test:
- Fresh database creation with migrations
- Migrating an old database schema
- Idempotent migration execution
- Creating policies with new fields

## How It Works

1. When `init_database()` is called (in `src/models/database.py`):
   - SQLAlchemy creates all tables based on current models
   - The migration manager is initialized
   - All pending migrations are run

2. The migration manager:
   - Creates a `schema_migrations` table if it doesn't exist
   - Checks which migrations have already been applied
   - Runs any pending migrations in order
   - Marks each migration as applied

3. Each migration:
   - Checks if columns exist before adding them
   - Uses ALTER TABLE to add missing columns
   - Sets appropriate default values
   - Logs all changes

## Troubleshooting

### Migration Failed
If a migration fails:
1. Check the logs for the specific error
2. The migration won't be marked as applied
3. Fix the issue and restart the application
4. The migration will be retried

### Column Already Exists
The migration system checks for existing columns before adding them, so this should never be an issue.

### Data Loss Concerns
Migrations only ADD columns, they never:
- Remove columns
- Modify existing column types
- Delete data

## Database Schema Tracking

The `schema_migrations` table tracks applied migrations:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version VARCHAR(50) UNIQUE NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

To see which migrations have been applied:

```bash
sqlite3 insurance.db "SELECT * FROM schema_migrations;"
```
