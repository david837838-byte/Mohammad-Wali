from datetime import datetime
from database.db_handler import get_db_connection
from .patient import Patient
from .user import User

class MedicalRecord:
    """نموذج السجل الطبي"""
    
    def __init__(self, id=None, patient_id=None, diagnosis="", treatment="", 
                 notes="", date=None, doctor_id=None, created_at=None, updated_at=None):
        self.id = id
        self.patient_id = patient_id
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.notes = notes
        self.date = date or datetime.now().date().isoformat()
        self.doctor_id = doctor_id
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
        
        # العلاقات
        self._patient = None
        self._doctor = None
    
    def to_dict(self):
        """تحويل الكائن إلى قاموس"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'notes': self.notes,
            'date': self.date,
            'doctor_id': self.doctor_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """إنشاء كائن من قاموس"""
        return MedicalRecord(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            diagnosis=data.get('diagnosis', ''),
            treatment=data.get('treatment', ''),
            notes=data.get('notes', ''),
            date=data.get('date'),
            doctor_id=data.get('doctor_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @property
    def patient(self):
        """الحصول على بيانات المريض"""
        if not self._patient and self.patient_id:
            self._patient = Patient.get_by_id(self.patient_id)
        return self._patient
    
    @property
    def doctor(self):
        """الحصول على بيانات الطبيب"""
        if not self._doctor and self.doctor_id:
            self._doctor = User.get_by_id(self.doctor_id)
        return self._doctor
    
    @staticmethod
    def get_all():
        """جلب جميع السجلات الطبية"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mr.*, p.name as patient_name, p.file_number as patient_file_number,
                   u.full_name as doctor_name
            FROM medical_records mr
            LEFT JOIN patients p ON mr.patient_id = p.id
            LEFT JOIN users u ON mr.doctor_id = u.id
            ORDER BY mr.date DESC, mr.created_at DESC
        ''')
        records_data = cursor.fetchall()
        conn.close()
        
        records = []
        for data in records_data:
            record = MedicalRecord.from_dict(dict(data))
            record._patient = {
                'name': data['patient_name'],
                'file_number': data['patient_file_number']
            }
            record._doctor = {'full_name': data['doctor_name']}
            records.append(record)
        
        return records
    
    @staticmethod
    def get_by_id(record_id):
        """جلب سجل طبي بواسطة المعرف"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mr.*, p.name as patient_name, p.file_number as patient_file_number,
                   u.full_name as doctor_name
            FROM medical_records mr
            LEFT JOIN patients p ON mr.patient_id = p.id
            LEFT JOIN users u ON mr.doctor_id = u.id
            WHERE mr.id = ?
        ''', (record_id,))
        record_data = cursor.fetchone()
        conn.close()
        
        if record_data:
            record = MedicalRecord.from_dict(dict(record_data))
            record._patient = {
                'name': record_data['patient_name'],
                'file_number': record_data['patient_file_number']
            }
            record._doctor = {'full_name': record_data['doctor_name']}
            return record
        return None
    
    @staticmethod
    def get_by_patient(patient_id):
        """جلب السجلات الطبية لمريض محدد"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mr.*, u.full_name as doctor_name
            FROM medical_records mr
            LEFT JOIN users u ON mr.doctor_id = u.id
            WHERE mr.patient_id = ?
            ORDER BY mr.date DESC, mr.created_at DESC
        ''', (patient_id,))
        records_data = cursor.fetchall()
        conn.close()
        
        records = []
        for data in records_data:
            record = MedicalRecord.from_dict(dict(data))
            record._doctor = {'full_name': data['doctor_name']}
            records.append(record)
        
        return records
    
    def save(self):
        """حفظ السجل الطبي (إضافة أو تحديث)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        self.updated_at = datetime.now().isoformat()
        
        if self.id:  # تحديث
            cursor.execute('''
                UPDATE medical_records 
                SET patient_id = ?, diagnosis = ?, treatment = ?, notes = ?, 
                    date = ?, doctor_id = ?, updated_at = ?
                WHERE id = ?
            ''', (
                self.patient_id, self.diagnosis, self.treatment, self.notes,
                self.date, self.doctor_id, self.updated_at, self.id
            ))
        else:  # إضافة
            cursor.execute('''
                INSERT INTO medical_records 
                (patient_id, diagnosis, treatment, notes, date, doctor_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.patient_id, self.diagnosis, self.treatment, self.notes,
                self.date, self.doctor_id, self.created_at, self.updated_at
            ))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """حذف السجل الطبي"""
        if not self.id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medical_records WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    @staticmethod
    def count():
        """عدد السجلات الطبية"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM medical_records')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def count_by_month(year, month):
        """عدد السجلات الطبية في شهر محدد"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM medical_records 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ''', (str(year), f"{month:02d}"))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_patient_name(self):
        """الحصول على اسم المريض"""
        if self.patient:
            return self.patient.name
        return "غير معروف"
    
    def get_doctor_name(self):
        """الحصول على اسم الطبيب"""
        if self.doctor:
            return self.doctor.full_name
        return "غير معروف"
    
    def get_formatted_date(self, format='%Y-%m-%d'):
        """الحصول على التاريخ بصيغة محددة"""
        try:
            date_obj = datetime.strptime(self.date, '%Y-%m-%d')
            return date_obj.strftime(format)
        except:
            return self.date