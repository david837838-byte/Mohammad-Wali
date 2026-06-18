from datetime import datetime
from database.db_handler import get_db_connection

class Invoice:
    """نموذج الفاتورة"""
    
    def __init__(self, id=None, invoice_number="", patient_id=None, visit_id=None, 
                 total_amount=0.0, paid_amount=0.0, status="غير مدفوع", 
                 date=None, created_at=None):
        self.id = id
        self.invoice_number = invoice_number
        self.patient_id = patient_id
        self.visit_id = visit_id
        self.total_amount = total_amount
        self.paid_amount = paid_amount
        self.status = status
        self.date = date or datetime.now().date().isoformat()
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.*, p.name as patient_name 
            FROM invoices i
            LEFT JOIN patients p ON i.patient_id = p.id
            ORDER BY i.date DESC
        ''')
        invoices = cursor.fetchall()
        conn.close()
        return [dict(i) for i in invoices]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not self.invoice_number:
            current_year = datetime.now().year
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE ?", (f'INV-{current_year}-%',))
            count = cursor.fetchone()[0] + 1
            self.invoice_number = f"INV-{current_year}-{count:04d}"
            
        if self.id:
            cursor.execute('''
                UPDATE invoices 
                SET total_amount = ?, paid_amount = ?, status = ?
                WHERE id = ?
            ''', (self.total_amount, self.paid_amount, self.status, self.id))
        else:
            cursor.execute('''
                INSERT INTO invoices (invoice_number, patient_id, visit_id, total_amount, paid_amount, status, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.invoice_number, self.patient_id, self.visit_id, self.total_amount, 
                  self.paid_amount, self.status, self.date, self.created_at))
            self.id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return self
