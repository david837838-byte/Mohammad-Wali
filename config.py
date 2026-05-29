import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hospital-management-system-secret-key-2024'
    SESSION_TYPE = 'filesystem'
    DATABASE = 'hospital.db'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    DEBUG = False
    
    # إعدادات Google Sheets (اختيارية)
    GOOGLE_SHEETS_ENABLED = False
    GOOGLE_SHEETS_CREDENTIALS_FILE = 'credentials.json'
    GOOGLE_SHEET_ID = '1_JvtLlgrN5GoNIIO7tP0eGsdd3sH9RXRLH7VlN8d9HM'
    GOOGLE_SCRIPT_URL = ''

class ProductionConfig(Config):
    """Configuration for production deployment"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

class DevelopmentConfig(Config):
    """Configuration for development"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuration for testing"""
    DEBUG = True
    TESTING = True
    DATABASE = ':memory:'