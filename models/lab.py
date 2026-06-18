from datetime import datetime
from database.db_handler import get_db_connection

class LabTest:
    """نموذج نوع التحليل"""
    
    def __init__(self, id=None, name="", category="", cost=0.0, normal_range="", 
                 status="متاح", created_at=None):
        self.id = id
        self.name = name
        self.category = category
        self.cost = cost
        self.normal_range = normal_range
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_tests ORDER BY name')
        tests = cursor.fetchall()
        conn.close()
        return [dict(t) for t in tests]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if self.id:
            cursor.execute('''
                UPDATE lab_tests 
                SET name = ?, category = ?, cost = ?, normal_range = ?, status = ?
                WHERE id = ?
            ''', (self.name, self.category, self.cost, self.normal_range, self.status, self.id))
        else:
            cursor.execute('''
                INSERT INTO lab_tests (name, category, cost, normal_range, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.name, self.category, self.cost, self.normal_range, self.status, self.created_at))
            self.id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return self

class LabRequest:
    """نموذج طلب التحليل"""
    
    def __init__(self, id=None, patient_id=None, visit_id=None, doctor_id=None, 
                 test_id=None, status="بانتظار العينة", result="", notes="", 
                 request_date=None, result_date=None):
        self.id = id
        self.patient_id = patient_id
        self.visit_id = visit_id
        self.doctor_id = doctor_id
        self.test_id = test_id
        self.status = status
        self.result = result
        self.notes = notes
        self.request_date = request_date or datetime.now().isoformat()
        self.result_date = result_date

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT lr.*, p.name as patient_name, u.full_name as doctor_name, lt.name as test_name 
            FROM lab_requests lr
            LEFT JOIN patients p ON lr.patient_id = p.id
            LEFT JOIN users u ON lr.doctor_id = u.id
            LEFT JOIN lab_tests lt ON lr.test_id = lt.id
            ORDER BY lr.request_date DESC
        ''')
        requests = cursor.fetchall()
        conn.close()
        return [dict(r) for r in requests]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if self.id:
            cursor.execute('''
                UPDATE lab_requests 
                SET status = ?, result = ?, notes = ?, result_date = ?
                WHERE id = ?
            ''', (self.status, self.result, self.notes, self.result_date, self.id))
        else:
            cursor.execute('''
                INSERT INTO lab_requests (patient_id, visit_id, doctor_id, test_id, status, result, notes, request_date, result_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.patient_id, self.visit_id, self.doctor_id, self.test_id, self.status, 
                  self.result, self.notes, self.request_date, self.result_date))
            self.id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return self
