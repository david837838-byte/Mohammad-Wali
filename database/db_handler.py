import sqlite3
import os
from datetime import datetime, date

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    # للعمل مع pythonanywhere: استخدم متغيرات البيئة
    db_url = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
    
    if db_url.startswith('sqlite'):
        # SQLite محلي
        # تحديد المسار المطلق لقاعدة البيانات لتجنب مشاكل مسار التشغيل
        BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(BASE_DIR, 'hospital.db')
        
        # إضافة timeout لتجنب "database is locked" error
        conn = sqlite3.connect(db_path, timeout=30.0)
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
    
    # -- بداية الجداول الجديدة --
    
    # جداول الصيدلية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            stock INTEGER DEFAULT 0,
            expiry_date TEXT,
            price REAL DEFAULT 0.0,
            status TEXT DEFAULT 'متوفر',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            visit_id INTEGER,
            doctor_id INTEGER NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'غير مصروف',
            date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (visit_id) REFERENCES visits (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescription_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            dosage TEXT NOT NULL,
            duration TEXT,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
            FOREIGN KEY (medicine_id) REFERENCES medicines (id)
        )
    ''')
    
    # جداول المالية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            visit_id INTEGER,
            total_amount REAL DEFAULT 0.0,
            paid_amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'غير مدفوع',
            date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (visit_id) REFERENCES visits (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL DEFAULT 0.0,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    # جداول المختبر
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            cost REAL DEFAULT 0.0,
            normal_range TEXT,
            status TEXT DEFAULT 'متاح',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            visit_id INTEGER,
            doctor_id INTEGER NOT NULL,
            test_id INTEGER NOT NULL,
            status TEXT DEFAULT 'بانتظار العينة',
            result TEXT,
            notes TEXT,
            request_date TEXT NOT NULL,
            result_date TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (visit_id) REFERENCES visits (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id),
            FOREIGN KEY (test_id) REFERENCES lab_tests (id)
        )
    ''')
    
    # -- نهاية الجداول الجديدة --

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