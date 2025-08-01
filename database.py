from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./budget_data.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BudgetData(Base):
    __tablename__ = "budget_data"
    
    id = Column(Integer, primary_key=True, index=True)
    business_unit = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    product_category = Column(String, nullable=False)
    region = Column(String, nullable=False)
    quarter = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Fixed columns (from PowerBI)
    historical_sales = Column(Float, nullable=True)
    target_sales = Column(Float, nullable=True)
    market_share = Column(Float, nullable=True)
    
    # Editable columns
    budget_amount = Column(Float, nullable=True)
    forecast_sales = Column(Float, nullable=True)
    comments = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    is_submitted = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_bu_user_quarter', 'business_unit', 'user_id', 'quarter', 'year'),
        Index('idx_submission_status', 'is_submitted', 'submitted_at'),
    )

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    business_unit = Column(String, nullable=False)
    session_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
