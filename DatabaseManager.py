from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from config import config

load_dotenv()

# Use config to get database URL (supports both SQLite and PostgreSQL)
DATABASE_URL = config.DATABASE_URL

# Configure engine based on database type
if DATABASE_URL.startswith('postgresql'):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        pool_size=10,
        max_overflow=20
    )
else:
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class China2025B(Base):
    __tablename__ = "China_2025B"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    business_unit = Column(String, nullable=False, index=True)
    Sales_Region = Column(String, nullable=True)
    Customer_Note = Column(String, nullable=True)
    Customer_Group = Column(String, nullable=True)
    BizType = Column(String, nullable=True)
    Vendor_Category = Column(String, nullable=True)
    Vendor_Grouping = Column(String, nullable=True)
    ProductNature = Column(String, nullable=True)
    Y2019A = Column(Float, nullable=True)
    Y2020A = Column(Float, nullable=True)
    Y2021A = Column(Float, nullable=True)
    Y2022A = Column(Float, nullable=True)
    Y2023A = Column(Float, nullable=True)
    Y2024B = Column(Float, nullable=True)
    Y2024Q3F = Column(Float, nullable=True)
    Y2024A08 = Column(Float, nullable=True)
    Y2024R08 = Column(Float, nullable=True)
    avg1924 = Column(Float, nullable=True)
    Y2025B = Column(Float, nullable=True)
    Y2026P = Column(Float, nullable=True)
    Y2027P = Column(Float, nullable=True)
    Y2028P = Column(Float, nullable=True)
    Y2029P = Column(Float, nullable=True)
    Sales_Remark = Column(String, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    business_unit = Column(String, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
    )

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()