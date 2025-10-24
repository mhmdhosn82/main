"""
Database initialization and management module for the Insurance Management System.
"""

import sqlite3
import os
from typing import Optional


class Database:
    """Database manager for the Insurance Management System."""
    
    def __init__(self, db_path: str = "insurance_data.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        
    def connect(self):
        """Establish connection to the database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            
    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        # Create insurance_policies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_number TEXT UNIQUE NOT NULL,
                insured_name TEXT NOT NULL,
                issuance_date TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                advance_payment REAL NOT NULL,
                total_installment_amount REAL NOT NULL,
                number_of_installments INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create installments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id INTEGER NOT NULL,
                installment_number INTEGER NOT NULL,
                due_date TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'unpaid',
                paid_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (policy_id) REFERENCES insurance_policies(id) ON DELETE CASCADE,
                UNIQUE(policy_id, installment_number)
            )
        """)
        
        # Create settings table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        
    def initialize(self):
        """Initialize the database with tables."""
        self.connect()
        self.create_tables()
        

def get_database() -> Database:
    """
    Get a database instance.
    
    Returns:
        Database instance
    """
    db = Database()
    db.initialize()
    return db
