from datetime import datetime
from database.db_handler import get_db_connection

class User:
    """نموذج المستخدم"""
    
    def __init__(self, id=None, full_name="", username="", password="", email="", 
                 phone="", role="view", status="نشط", created_at=None, updated_at=None):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at
    
    def to_dict(self):
        """تحويل الكائن إلى قاموس"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """إنشاء كائن من قاموس"""
        return User(
            id=data.get('id'),
            full_name=data.get('full_name', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            role=data.get('role', 'view'),
            status=data.get('status', 'نشط'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def get_all():
        """جلب جميع المستخدمين"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users_data = cursor.fetchall()
        conn.close()
        
        return [User.from_dict(dict(user)) for user in users_data]
    
    @staticmethod
    def get_by_id(user_id):
        """جلب مستخدم بواسطة المعرف"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User.from_dict(dict(user_data))
        return None
    
    @staticmethod
    def get_by_username(username):
        """جلب مستخدم بواسطة اسم المستخدم"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User.from_dict(dict(user_data))
        return None
    
    @staticmethod
    def authenticate(username, password):
        """مصادقة المستخدم"""
        user = User.get_by_username(username)
        if user and user.password == password and user.status == 'نشط':
            return user
        return None
    
    def save(self):
        """حفظ المستخدم (إضافة أو تحديث)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        self.updated_at = datetime.now().isoformat()
        
        if self.id:  # تحديث
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, username = ?, password = ?, email = ?, 
                    phone = ?, role = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (
                self.full_name, self.username, self.password, self.email,
                self.phone, self.role, self.status, self.updated_at, self.id
            ))
        else:  # إضافة
            cursor.execute('''
                INSERT INTO users 
                (full_name, username, password, email, phone, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.full_name, self.username, self.password, self.email,
                self.phone, self.role, self.status, self.created_at, self.updated_at
            ))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """حذف المستخدم"""
        if not self.id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    @staticmethod
    def count_by_role(role):
        """عدد المستخدمين حسب الدور"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', (role,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def get_active_users():
        """جلب المستخدمين النشطين"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE status = 'نشط' ORDER BY full_name")
        users_data = cursor.fetchall()
        conn.close()
        
        return [User.from_dict(dict(user)) for user in users_data]
    
    def get_role_display(self):
        """الحصول على اسم الدور بالعربية"""
        roles = {
            'admin': 'مدير النظام',
            'doctor': 'طبيب',
            'nurse': 'ممرض/ممرضة',
            'view': 'مشاهد فقط'
        }
        return roles.get(self.role, self.role)
    
    def is_admin(self):
        """التحقق إذا كان المستخدم مدير"""
        return self.role == 'admin'
    
    def is_doctor(self):
        """التحقق إذا كان المستخدم طبيب"""
        return self.role == 'doctor'
    
    def is_nurse(self):
        """التحقق إذا كان المستخدم ممرض"""
        return self.role == 'nurse'
    
    def can_edit_patients(self):
        """التحقق إذا كان يمكن للمستخدم تعديل المرضى"""
        return self.role in ['admin', 'doctor', 'nurse']
    
    def can_edit_users(self):
        """التحقق إذا كان يمكن للمستخدم تعديل المستخدمين"""
        return self.role == 'admin'
    
    def can_access_settings(self):
        """التحقق إذا كان يمكن للمستخدم الوصول للإعدادات"""
        return self.role in ['admin', 'doctor']