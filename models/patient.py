from datetime import datetime
from database.db_handler import get_db_connection

class Patient:
    """نموذج المريض"""
    
    def __init__(self, id=None, file_number="", name="", age=0, gender="", 
                 phone="", address="", diagnosis="", status="نشط", 
                 created_at=None, updated_at=None):
        self.id = id
        self.file_number = file_number
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.address = address
        self.diagnosis = diagnosis
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
    
    def to_dict(self):
        """تحويل الكائن إلى قاموس"""
        return {
            'id': self.id,
            'file_number': self.file_number,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'diagnosis': self.diagnosis,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """إنشاء كائن من قاموس"""
        return Patient(
            id=data.get('id'),
            file_number=data.get('file_number', ''),
            name=data.get('name', ''),
            age=data.get('age', 0),
            gender=data.get('gender', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            diagnosis=data.get('diagnosis', ''),
            status=data.get('status', 'نشط'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def get_all():
        """جلب جميع المرضى"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients ORDER BY created_at DESC')
        patients_data = cursor.fetchall()
        conn.close()
        
        return [Patient.from_dict(dict(patient)) for patient in patients_data]
    
    @staticmethod
    def get_by_id(patient_id):
        """جلب مريض بواسطة المعرف"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
        patient_data = cursor.fetchone()
        conn.close()
        
        if patient_data:
            return Patient.from_dict(dict(patient_data))
        return None
    
    @staticmethod
    def get_by_file_number(file_number):
        """جلب مريض بواسطة رقم الملف"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE file_number = ?', (file_number,))
        patient_data = cursor.fetchone()
        conn.close()
        
        if patient_data:
            return Patient.from_dict(dict(patient_data))
        return None
    
    @staticmethod
    def search(query):
        """بحث في المرضى"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM patients 
            WHERE name LIKE ? OR file_number LIKE ? OR phone LIKE ?
            ORDER BY name
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        patients_data = cursor.fetchall()
        conn.close()
        
        return [Patient.from_dict(dict(patient)) for patient in patients_data]
    
    def save(self):
        """حفظ المريض (إضافة أو تحديث)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        self.updated_at = datetime.now().isoformat()
        
        if self.id:  # تحديث
            cursor.execute('''
                UPDATE patients 
                SET file_number = ?, name = ?, age = ?, gender = ?, phone = ?, 
                    address = ?, diagnosis = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (
                self.file_number, self.name, self.age, self.gender, self.phone,
                self.address, self.diagnosis, self.status, self.updated_at, self.id
            ))
        else:  # إضافة
            # توليد رقم ملف جديد إذا لم يكن موجوداً
            if not self.file_number:
                self.file_number = self.generate_file_number()
            
            cursor.execute('''
                INSERT INTO patients 
                (file_number, name, age, gender, phone, address, diagnosis, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.file_number, self.name, self.age, self.gender, self.phone,
                self.address, self.diagnosis, self.status, self.created_at, self.updated_at
            ))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def generate_file_number(self):
        """توليد رقم ملف جديد"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_year = datetime.now().year
        cursor.execute('''
            SELECT COUNT(*) FROM patients 
            WHERE file_number LIKE ? AND strftime('%Y', created_at) = ?
        ''', (f'PT-{current_year}-%', str(current_year)))
        
        count = cursor.fetchone()[0] + 1
        conn.close()
        
        return f"PT-{current_year}-{count:03d}"
    
    def delete(self):
        """حذف المريض"""
        if not self.id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patients WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    @staticmethod
    def count():
        """عدد المرضى"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM patients')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def count_by_gender(gender):
        """عدد المرضى حسب الجنس"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM patients WHERE gender = ?', (gender,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def count_by_status(status):
        """عدد المرضى حسب الحالة"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM patients WHERE status = ?', (status,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def get_recent(limit=5):
        """جلب أحدث المرضى"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients ORDER BY created_at DESC LIMIT ?', (limit,))
        patients_data = cursor.fetchall()
        conn.close()
        
        return [Patient.from_dict(dict(patient)) for patient in patients_data]
    
    def get_age_group(self):
        """الحصول على الفئة العمرية"""
        if self.age < 18:
            return "طفل"
        elif self.age < 30:
            return "شاب"
        elif self.age < 60:
            return "بالغ"
        else:
            return "مسن"
    
    def is_active(self):
        """التحقق إذا كان المريض نشط"""
        return self.status == 'نشط'
    
    def get_status_class(self):
        """الحصول على كلاس الحالة"""
        classes = {
            'نشط': 'status-active',
            'بانتظار الفحص': 'status-pending',
            'غير نشط': 'status-inactive'
        }
        return classes.get(self.status, '')
    
    def get_gender_display(self):
        """الحصول على الجنس بالعربية"""
        genders = {
            'ذكر': 'ذكر',
            'أنثى': 'أنثى',
            'male': 'ذكر',
            'female': 'أنثى'
        }
        return genders.get(self.gender, self.gender)