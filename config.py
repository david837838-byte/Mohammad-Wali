import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hospital-management-system-secret-key-2024'
    SESSION_TYPE = 'filesystem'
    DATABASE = 'hospital.db'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # إعدادات Google Sheets (اختيارية)
    GOOGLE_SHEETS_ENABLED = False
    GOOGLE_SHEETS_CREDENTIALS_FILE = 'credentials.json'
    GOOGLE_SHEET_ID = '1_JvtLlgrN5GoNIIO7tP0eGsdd3sH9RXRLH7VlN8d9HM'
    GOOGLE_SCRIPT_URL = ''