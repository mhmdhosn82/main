"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'insurance.db')

engine = None
SessionLocal = None

def init_database():
    """Initialize database and create all tables"""
    global engine, SessionLocal
    
    engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
    SessionLocal = sessionmaker(bind=engine)
    
    # Import all models to ensure they're registered
    from . import user, policy, installment, reminder
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations to update existing database schema
    try:
        from ..migrations import MigrationManager
        migration_manager = MigrationManager(DB_PATH)
        migration_manager.run_migrations()
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        # Don't fail initialization if migrations fail - let the app continue
        # This allows the app to work even if migrations have issues
    
    return engine

def get_session():
    """Get a new database session"""
    if SessionLocal is None:
        init_database()
    return SessionLocal()
