from datetime import datetime, time
from database.db_handler import get_db_connection
from .patient import Patient
from .user import User

class Visit:
    """نموذج الزيارة"""
    
    def __init__(self, id=None, patient_id=None, date=None, time_str="", 
                 purpose="", diagnosis="", prescription="", status="مجدول",
                 doctor_id=None, created_at=None, updated_at=None):
        self.id = id
        self.patient_id = patient_id
        self.date = date or datetime.now().date().isoformat()
        self.time_str = time_str or datetime.now().strftime("%H:%M")
        self.purpose = purpose
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.status = status
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
            'date': self.date,
            'time': self.time_str,
            'purpose': self.purpose,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'status': self.status,
            'doctor_id': self.doctor_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """إنشاء كائن من قاموس"""
        return Visit(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            date=data.get('date'),
            time_str=data.get('time', ''),
            purpose=data.get('purpose', ''),
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            status=data.get('status', 'مجدول'),
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
        """جلب جميع الزيارات"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, p.name as patient_name, p.file_number as patient_file_number,
                   u.full_name as doctor_name
            FROM visits v
            LEFT JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.doctor_id = u.id
            ORDER BY v.date DESC, v.time DESC
        ''')
        visits_data = cursor.fetchall()
        conn.close()
        
        visits = []
        for data in visits_data:
            visit = Visit.from_dict(dict(data))
            visit._patient = {
                'name': data['patient_name'],
                'file_number': data['patient_file_number']
            }
            visit._doctor = {'full_name': data['doctor_name']}
            visits.append(visit)
        
        return visits
    
    @staticmethod
    def get_by_id(visit_id):
        """جلب زيارة بواسطة المعرف"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, p.name as patient_name, p.file_number as patient_file_number,
                   u.full_name as doctor_name
            FROM visits v
            LEFT JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.doctor_id = u.id
            WHERE v.id = ?
        ''', (visit_id,))
        visit_data = cursor.fetchone()
        conn.close()
        
        if visit_data:
            visit = Visit.from_dict(dict(visit_data))
            visit._patient = {
                'name': visit_data['patient_name'],
                'file_number': visit_data['patient_file_number']
            }
            visit._doctor = {'full_name': visit_data['doctor_name']}
            return visit
        return None
    
    @staticmethod
    def get_today():
        """جلب زيارات اليوم"""
        today = datetime.now().date().isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, p.name as patient_name, p.file_number as patient_file_number,
                   u.full_name as doctor_name
            FROM visits v
            LEFT JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.doctor_id = u.id
            WHERE v.date = ?
            ORDER BY v.time
        ''', (today,))
        visits_data = cursor.fetchall()
        conn.close()
        
        visits = []
        for data in visits_data:
            visit = Visit.from_dict(dict(data))
            visit._patient = {
                'name': data['patient_name'],
                'file_number': data['patient_file_number']
            }
            visit._doctor = {'full_name': data['doctor_name']}
            visits.append(visit)
        
        return visits
    
    @staticmethod
    def get_by_patient(patient_id):
        """جلب زيارات مريض محدد"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, u.full_name as doctor_name
            FROM visits v
            LEFT JOIN users u ON v.doctor_id = u.id
            WHERE v.patient_id = ?
            ORDER BY v.date DESC, v.time DESC
        ''', (patient_id,))
        visits_data = cursor.fetchall()
        conn.close()
        
        visits = []
        for data in visits_data:
            visit = Visit.from_dict(dict(data))
            visit._doctor = {'full_name': data['doctor_name']}
            visits.append(visit)
        
        return visits
    
    def save(self):
        """حفظ الزيارة (إضافة أو تحديث)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        self.updated_at = datetime.now().isoformat()
        
        if self.id:  # تحديث
            cursor.execute('''
                UPDATE visits 
                SET patient_id = ?, date = ?, time = ?, purpose = ?, 
                    diagnosis = ?, prescription = ?, status = ?, 
                    doctor_id = ?, updated_at = ?
                WHERE id = ?
            ''', (
                self.patient_id, self.date, self.time_str, self.purpose,
                self.diagnosis, self.prescription, self.status,
                self.doctor_id, self.updated_at, self.id
            ))
        else:  # إضافة
            cursor.execute('''
                INSERT INTO visits 
                (patient_id, date, time, purpose, diagnosis, prescription, 
                 status, doctor_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.patient_id, self.date, self.time_str, self.purpose,
                self.diagnosis, self.prescription, self.status,
                self.doctor_id, self.created_at, self.updated_at
            ))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """حذف الزيارة"""
        if not self.id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM visits WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    @staticmethod
    def count():
        """عدد الزيارات"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM visits')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def count_today():
        """عدد زيارات اليوم"""
        today = datetime.now().date().isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM visits WHERE date = ?', (today,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def count_by_status(status):
        """عدد الزيارات حسب الحالة"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM visits WHERE status = ?', (status,))
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
    
    def get_status_class(self):
        """الحصول على كلاس الحالة"""
        classes = {
            'مجدول': 'status-pending',
            'مكتمل': 'status-active',
            'ملغى': 'status-inactive'
        }
        return classes.get(self.status, '')
    
    def is_completed(self):
        """التحقق إذا كانت الزيارة مكتملة"""
        return self.status == 'مكتمل'
    
    def is_scheduled(self):
        """التحقق إذا كانت الزيارة مجدولة"""
        return self.status == 'مجدول'
    
    def is_cancelled(self):
        """التحقق إذا كانت الزيارة ملغية"""
        return self.status == 'ملغى'