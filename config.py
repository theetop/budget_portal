import os
from typing import Optional

# Try to import streamlit for secrets management
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from Streamlit secrets or environment variables"""
    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        try:
            # Try to get from streamlit secrets first
            parts = key.split('.')
            value = st.secrets
            for part in parts:
                value = value.get(part)
                if value is None:
                    break
            if value is not None:
                return str(value)
        except (KeyError, AttributeError):
            pass
    
    # Fallback to environment variables
    return os.getenv(key.replace('.', '_').upper(), default)

class Config:
    """Application configuration"""
    
    # Environment detection
    ENVIRONMENT = get_secret("general.ENVIRONMENT", "development")
    
    # API Configuration
    API_HOST = get_secret("API_HOST", "127.0.0.1") or "127.0.0.1"
    API_PORT = int(get_secret("API_PORT", "8000") or "8000")
    
    # Database Configuration
    DATABASE_URL = get_secret("database.DATABASE_URL", "sqlite:///./budget_data.db") or "sqlite:///./budget_data.db"
    
    # PowerBI Configuration
    POWERBI_CLIENT_ID = get_secret("powerbi.POWERBI_CLIENT_ID")
    POWERBI_CLIENT_SECRET = get_secret("powerbi.POWERBI_CLIENT_SECRET")
    POWERBI_TENANT_ID = get_secret("powerbi.POWERBI_TENANT_ID")
    POWERBI_WORKSPACE_ID = get_secret("powerbi.POWERBI_WORKSPACE_ID")
    POWERBI_DATASET_ID = get_secret("powerbi.POWERBI_DATASET_ID")
    
    # Security
    SECRET_KEY = get_secret("security.SECRET_KEY", "your-secret-key-change-in-production") or "your-secret-key-change-in-production"
    SESSION_TIMEOUT_HOURS = int(get_secret("security.SESSION_TIMEOUT_HOURS", "8") or "8")
    
    @classmethod
    def get_api_base_url(cls) -> str:
        """Get the API base URL based on environment"""
        # First try to get from secrets/env
        api_url = get_secret("general.API_BASE_URL")
        if api_url:
            return api_url
        
        # Fallback to environment-based logic
        if cls.ENVIRONMENT == "production":
            return "https://your-backend-app.onrender.com"
        elif cls.ENVIRONMENT == "staging":
            return "https://your-backend-staging.onrender.com"
        else:
            # Development
            return f"http://{cls.API_HOST}:{cls.API_PORT}"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENVIRONMENT == "development"

# Global config instance
config = Config()
