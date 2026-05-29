import sqlite3
import os
from datetime import datetime, date

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    # للعمل مع pythonanywhere: استخدم متغيرات البيئة
    db_url = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
    
    if db_url.startswith('sqlite'):
        # SQLite محلي
        # إضافة timeout لتجنب "database is locked" error
        conn = sqlite3.connect('hospital.db', timeout=30.0)
        conn.row_factory = sqlite3.Row
        # تحسين الأداء
        conn.execute('PRAGMA journal_mode=WAL')
    else:
        # PostgreSQL (لـ pythonanywhere)
        import psycopg2
        conn = psycopg2.connect(db_url)
    
    return conn

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'نشط',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # جدول الصلاحيات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            can_view_patients BOOLEAN DEFAULT 0,
            can_add_patients BOOLEAN DEFAULT 0,
            can_edit_patients BOOLEAN DEFAULT 0,
            can_delete_patients BOOLEAN DEFAULT 0,
            can_view_medical BOOLEAN DEFAULT 0,
            can_add_medical BOOLEAN DEFAULT 0,
            can_edit_medical BOOLEAN DEFAULT 0,
            can_delete_medical BOOLEAN DEFAULT 0,
            can_view_visits BOOLEAN DEFAULT 0,
            can_add_visits BOOLEAN DEFAULT 0,
            can_edit_visits BOOLEAN DEFAULT 0,
            can_delete_visits BOOLEAN DEFAULT 0,
            can_view_reports BOOLEAN DEFAULT 0,
            can_manage_users BOOLEAN DEFAULT 0,
            can_manage_settings BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول المرضى
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            diagnosis TEXT,
            status TEXT DEFAULT 'نشط',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # جدول السجلات الطبية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            notes TEXT,
            date TEXT NOT NULL,
            doctor_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    ''')
    
    # جدول الزيارات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            purpose TEXT,
            diagnosis TEXT,
            prescription TEXT,
            status TEXT DEFAULT 'مجدول',
            doctor_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    ''')
    
    # جدول الإعدادات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            script_url TEXT,
            sheet_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # جدول السجلات (للتدقيق)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            details TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_sample_data():
    """إضافة بيانات تجريبية"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من وجود بيانات
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # إضافة مستخدمين تجريبيين
        sample_users = [
            ('مدير النظام', 'admin', 'admin123', 'admin@hospital.com', '0512345678', 'admin', 'نشط'),
            ('د. محمد أحمد', 'doctor1', 'doctor123', 'doctor@hospital.com', '0523456789', 'doctor', 'نشط'),
            ('ممرضة سارة', 'nurse1', 'nurse123', 'nurse@hospital.com', '0534567890', 'nurse', 'نشط'),
            ('مشاهد النظام', 'viewer', 'view123', 'viewer@hospital.com', '0545678901', 'view', 'نشط')
        ]
        
        current_date = date.today().isoformat()
        for user in sample_users:
            cursor.execute('''
                INSERT INTO users (full_name, username, password, email, phone, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', user + (current_date,))
        
        # إضافة مرضى تجريبيين
        sample_patients = [
            ('PT-2024-001', 'أحمد محمود', 42, 'ذكر', '0512345678', 'الرياض - حي الملك فهد', 'ارتفاع ضغط الدم', 'نشط'),
            ('PT-2024-002', 'فاطمة خالد', 35, 'أنثى', '0523456789', 'جدة - حي الصفا', 'سكري النوع الثاني', 'نشط'),
            ('PT-2024-003', 'سعيد حسن', 58, 'ذكر', '0534567890', 'الدمام - حي الثقبة', 'أمراض القلب', 'بانتظار الفحص'),
            ('PT-2024-004', 'نورة سليم', 29, 'أنثى', '0545678901', 'الرياض - حي النخيل', 'حساسية الربيع', 'نشط'),
            ('PT-2024-005', 'خالد عبدالله', 45, 'ذكر', '0556789012', 'الخرج - حي اليمامة', 'آلام الظهر', 'غير نشط')
        ]
        
        for patient in sample_patients:
            cursor.execute('''
                INSERT INTO patients (file_number, name, age, gender, phone, address, diagnosis, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', patient + (current_date,))
        
        conn.commit()
    
    conn.close()