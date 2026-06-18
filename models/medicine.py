from datetime import datetime
from database.db_handler import get_db_connection

class Medicine:
    """نموذج الدواء"""
    
    def __init__(self, id=None, name="", category="", stock=0, expiry_date="", 
                 price=0.0, status="متوفر", created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.category = category
        self.stock = stock
        self.expiry_date = expiry_date
        self.price = price
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'stock': self.stock,
            'expiry_date': self.expiry_date,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        return Medicine(
            id=data.get('id'),
            name=data.get('name', ''),
            category=data.get('category', ''),
            stock=data.get('stock', 0),
            expiry_date=data.get('expiry_date', ''),
            price=data.get('price', 0.0),
            status=data.get('status', 'متوفر'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medicines ORDER BY name')
        medicines = cursor.fetchall()
        conn.close()
        return [Medicine.from_dict(dict(m)) for m in medicines]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        self.updated_at = datetime.now().isoformat()
        
        if self.id:
            cursor.execute('''
                UPDATE medicines 
                SET name = ?, category = ?, stock = ?, expiry_date = ?, 
                    price = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (self.name, self.category, self.stock, self.expiry_date, 
                  self.price, self.status, self.updated_at, self.id))
        else:
            cursor.execute('''
                INSERT INTO medicines (name, category, stock, expiry_date, price, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.name, self.category, self.stock, self.expiry_date, 
                  self.price, self.status, self.created_at, self.updated_at))
            self.id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return self

class Prescription:
    """نموذج الوصفة الطبية"""
    def __init__(self, id=None, patient_id=None, visit_id=None, doctor_id=None, 
                 notes="", status="غير مصروف", date=None, created_at=None):
        self.id = id
        self.patient_id = patient_id
        self.visit_id = visit_id
        self.doctor_id = doctor_id
        self.notes = notes
        self.status = status
        self.date = date or datetime.now().date().isoformat()
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, pat.name as patient_name, doc.full_name as doctor_name 
            FROM prescriptions p
            LEFT JOIN patients pat ON p.patient_id = pat.id
            LEFT JOIN users doc ON p.doctor_id = doc.id
            ORDER BY p.date DESC
        ''')
        prescriptions = cursor.fetchall()
        conn.close()
        return [dict(p) for p in prescriptions]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute('''
                UPDATE prescriptions 
                SET notes = ?, status = ?
                WHERE id = ?
            ''', (self.notes, self.status, self.id))
        else:
            cursor.execute('''
                INSERT INTO prescriptions (patient_id, visit_id, doctor_id, notes, status, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.patient_id, self.visit_id, self.doctor_id, self.notes, self.status, self.date, self.created_at))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self
