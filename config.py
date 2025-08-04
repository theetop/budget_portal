import os
from typing import Optional

class Config:
    def __init__(self):
        # Environment detection
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        
        # API Configuration
        if self.is_production():
            self.API_BASE_URL = os.getenv('API_BASE_URL', 'https://your-app.onrender.com')
        else:
            self.API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
        
        # Database Configuration
        self.DATABASE_URL = self._get_database_url()
        
        # PowerBI Configuration
        self.POWERBI_CLIENT_ID = os.getenv('POWERBI_CLIENT_ID', '')
        self.POWERBI_CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET', '')
        self.POWERBI_TENANT_ID = os.getenv('POWERBI_TENANT_ID', '')
        self.POWERBI_WORKSPACE_ID = os.getenv('POWERBI_WORKSPACE_ID', '')
        self.POWERBI_DATASET_ID = os.getenv('POWERBI_DATASET_ID', '')
        
        # Security
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', '8'))

    def _get_database_url(self) -> str:
        """Get database URL based on environment"""
        # Check for Railway PostgreSQL first
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Railway provides DATABASE_URL, use it directly
            return database_url
        
        # Fallback to individual components
        if self.is_production():
            # Try to construct from individual env vars
            host = os.getenv('DB_HOST', 'switchyard.proxy.rlwy.net')
            port = os.getenv('DB_PORT', '39585')
            database = os.getenv('DB_NAME', 'railway')
            username = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASSWORD', '')
            
            if password:
                return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        # Default to SQLite for development
        return "sqlite:///./China_2025B.db"

    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == 'production'
    
    def get_api_base_url(self) -> str:
        return self.API_BASE_URL

# Global config instance
config = Config()