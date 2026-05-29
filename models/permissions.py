from datetime import datetime
from database.db_handler import get_db_connection

class UserPermissions:
    """نموذج إدارة صلاحيات المستخدمين"""
    
    def __init__(self, user_id, can_view_patients=False, can_add_patients=False,
                 can_edit_patients=False, can_delete_patients=False,
                 can_view_medical=False, can_add_medical=False,
                 can_edit_medical=False, can_delete_medical=False,
                 can_view_visits=False, can_add_visits=False,
                 can_edit_visits=False, can_delete_visits=False,
                 can_view_reports=False, can_manage_users=False,
                 can_manage_settings=False):
        self.user_id = user_id
        self.can_view_patients = can_view_patients
        self.can_add_patients = can_add_patients
        self.can_edit_patients = can_edit_patients
        self.can_delete_patients = can_delete_patients
        self.can_view_medical = can_view_medical
        self.can_add_medical = can_add_medical
        self.can_edit_medical = can_edit_medical
        self.can_delete_medical = can_delete_medical
        self.can_view_visits = can_view_visits
        self.can_add_visits = can_add_visits
        self.can_edit_visits = can_edit_visits
        self.can_delete_visits = can_delete_visits
        self.can_view_reports = can_view_reports
        self.can_manage_users = can_manage_users
        self.can_manage_settings = can_manage_settings
    
    @staticmethod
    def get_default_permissions(role):
        """الحصول على الصلاحيات الافتراضية حسب الدور"""
        permissions = {
            'admin': {
                'can_view_patients': True,
                'can_add_patients': True,
                'can_edit_patients': True,
                'can_delete_patients': True,
                'can_view_medical': True,
                'can_add_medical': True,
                'can_edit_medical': True,
                'can_delete_medical': True,
                'can_view_visits': True,
                'can_add_visits': True,
                'can_edit_visits': True,
                'can_delete_visits': True,
                'can_view_reports': True,
                'can_manage_users': True,
                'can_manage_settings': True
            },
            'doctor': {
                'can_view_patients': True,
                'can_add_patients': False,
                'can_edit_patients': False,
                'can_delete_patients': False,
                'can_view_medical': True,
                'can_add_medical': True,
                'can_edit_medical': True,
                'can_delete_medical': False,
                'can_view_visits': True,
                'can_add_visits': True,
                'can_edit_visits': True,
                'can_delete_visits': False,
                'can_view_reports': True,
                'can_manage_users': False,
                'can_manage_settings': False
            },
            'nurse': {
                'can_view_patients': True,
                'can_add_patients': False,
                'can_edit_patients': False,
                'can_delete_patients': False,
                'can_view_medical': True,
                'can_add_medical': False,
                'can_edit_medical': False,
                'can_delete_medical': False,
                'can_view_visits': True,
                'can_add_visits': False,
                'can_edit_visits': False,
                'can_delete_visits': False,
                'can_view_reports': False,
                'can_manage_users': False,
                'can_manage_settings': False
            },
            'view': {
                'can_view_patients': True,
                'can_add_patients': False,
                'can_edit_patients': False,
                'can_delete_patients': False,
                'can_view_medical': True,
                'can_add_medical': False,
                'can_edit_medical': False,
                'can_delete_medical': False,
                'can_view_visits': True,
                'can_add_visits': False,
                'can_edit_visits': False,
                'can_delete_visits': False,
                'can_view_reports': False,
                'can_manage_users': False,
                'can_manage_settings': False
            }
        }
        return permissions.get(role, permissions['view'])
    
    @staticmethod
    def create_for_user(user_id, role='view'):
        """إنشاء صلاحيات للمستخدم الجديد"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        default_perms = UserPermissions.get_default_permissions(role)
        
        try:
            cursor.execute('''
                INSERT INTO user_permissions 
                (user_id, can_view_patients, can_add_patients, can_edit_patients, 
                 can_delete_patients, can_view_medical, can_add_medical, can_edit_medical,
                 can_delete_medical, can_view_visits, can_add_visits, can_edit_visits,
                 can_delete_visits, can_view_reports, can_manage_users, can_manage_settings,
                 created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                default_perms['can_view_patients'],
                default_perms['can_add_patients'],
                default_perms['can_edit_patients'],
                default_perms['can_delete_patients'],
                default_perms['can_view_medical'],
                default_perms['can_add_medical'],
                default_perms['can_edit_medical'],
                default_perms['can_delete_medical'],
                default_perms['can_view_visits'],
                default_perms['can_add_visits'],
                default_perms['can_edit_visits'],
                default_perms['can_delete_visits'],
                default_perms['can_view_reports'],
                default_perms['can_manage_users'],
                default_perms['can_manage_settings'],
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            print(f"خطأ: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """الحصول على صلاحيات المستخدم"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_permissions WHERE user_id = ?', (user_id,))
        perms = cursor.fetchone()
        conn.close()
        
        if perms:
            return dict(perms)
        return None
    
    @staticmethod
    def update_permissions(user_id, permissions_dict):
        """تحديث صلاحيات المستخدم"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بناء استعلام التحديث ديناميكياً
        columns = []
        values = []
        for key, value in permissions_dict.items():
            if key != 'user_id':
                columns.append(f"{key} = ?")
                values.append(value)
        
        values.append(datetime.now().isoformat())
        values.append(user_id)
        
        if columns:
            query = f"UPDATE user_permissions SET {', '.join(columns)}, updated_at = ? WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def has_permission(user_id, permission):
        """التحقق من وجود صلاحية معينة للمستخدم"""
        perms = UserPermissions.get_by_user_id(user_id)
        if perms:
            return perms.get(permission, False)
        return False
    
    def to_dict(self):
        """تحويل الصلاحيات إلى قاموس"""
        return {
            'user_id': self.user_id,
            'can_view_patients': self.can_view_patients,
            'can_add_patients': self.can_add_patients,
            'can_edit_patients': self.can_edit_patients,
            'can_delete_patients': self.can_delete_patients,
            'can_view_medical': self.can_view_medical,
            'can_add_medical': self.can_add_medical,
            'can_edit_medical': self.can_edit_medical,
            'can_delete_medical': self.can_delete_medical,
            'can_view_visits': self.can_view_visits,
            'can_add_visits': self.can_add_visits,
            'can_edit_visits': self.can_edit_visits,
            'can_delete_visits': self.can_delete_visits,
            'can_view_reports': self.can_view_reports,
            'can_manage_users': self.can_manage_users,
            'can_manage_settings': self.can_manage_settings
        }
