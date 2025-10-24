"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

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
    
    return engine

def get_session():
    """Get a new database session"""
    if SessionLocal is None:
        init_database()
    return SessionLocal()
