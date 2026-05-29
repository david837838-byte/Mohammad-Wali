"""
أدوات مساعدة عامة
"""

import os
import json
import random
import string
from datetime import datetime, timedelta, date
from flask import session, request
import pandas as pd
import io

class Helpers:
    """فئة الأدوات المساعدة"""
    
    @staticmethod
    def generate_random_string(length=8):
        """
        توليد نص عشوائي
        
        Args:
            length: طول النص
        
        Returns:
            str: نص عشوائي
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_file_number(prefix='PT', year=None):
        """
        توليد رقم ملف
        
        Args:
            prefix: البادئة
            year: السنة (اختياري)
        
        Returns:
            str: رقم الملف
        """
        if year is None:
            year = datetime.now().year
        
        random_part = ''.join(random.choice(string.digits) for _ in range(4))
        return f"{prefix}-{year}-{random_part}"
    
    @staticmethod
    def format_date(date_obj, format_str='%Y-%m-%d'):
        """
        تنسيق التاريخ
        
        Args:
            date_obj: كائن التاريخ
            format_str: تنسيق التاريخ
        
        Returns:
            str: التاريخ المنسق
        """
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
            except ValueError:
                return date_obj
        
        if isinstance(date_obj, (datetime, date)):
            return date_obj.strftime(format_str)
        
        return str(date_obj)
    
    @staticmethod
    def format_datetime(datetime_obj, format_str='%Y-%m-%d %H:%M'):
        """
        تنسيق التاريخ والوقت
        
        Args:
            datetime_obj: كائن التاريخ والوقت
            format_str: التنسيق
        
        Returns:
            str: التاريخ والوقت المنسقين
        """
        if isinstance(datetime_obj, str):
            try:
                datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
            except ValueError:
                return datetime_obj
        
        if isinstance(datetime_obj, datetime):
            return datetime_obj.strftime(format_str)
        
        return str(datetime_obj)
    
    @staticmethod
    def get_arabic_date(date_obj=None):
        """
        الحصول على التاريخ بالعربية
        
        Args:
            date_obj: كائن التاريخ (اختياري)
        
        Returns:
            str: التاريخ بالعربية
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
            except ValueError:
                return date_obj
        
        days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
                 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        
        day_name = days[date_obj.weekday()]
        day = date_obj.day
        month = months[date_obj.month - 1]
        year = date_obj.year
        
        return f"{day_name} {day} {month} {year}"
    
    @staticmethod
    def get_arabic_datetime(datetime_obj=None):
        """
        الحصول على التاريخ والوقت بالعربية
        
        Args:
            datetime_obj: كائن التاريخ والوقت (اختياري)
        
        Returns:
            str: التاريخ والوقت بالعربية
        """
        if datetime_obj is None:
            datetime_obj = datetime.now()
        
        date_str = Helpers.get_arabic_date(datetime_obj)
        time_str = datetime_obj.strftime("%I:%M %p")
        
        # تحويل AM/PM إلى صباحاً/مساءً
        time_str = time_str.replace('AM', 'صباحاً').replace('PM', 'مساءً')
        
        return f"{date_str} - {time_str}"
    
    @staticmethod
    def calculate_age(birth_date):
        """
        حساب العمر من تاريخ الميلاد
        
        Args:
            birth_date: تاريخ الميلاد
        
        Returns:
            int: العمر
        """
        if isinstance(birth_date, str):
            try:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                return 0
        
        today = date.today()
        
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        elif isinstance(birth_date, date):
            pass
        else:
            return 0
        
        age = today.year - birth_date.year
        
        # التحقق إذا لم يأتي عيد الميلاد بعد هذا السنة
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    @staticmethod
    def get_time_ago(datetime_obj):
        """
        الحصول على الوقت الماضي منذ تاريخ معين
        
        Args:
            datetime_obj: كائن التاريخ والوقت
        
        Returns:
            str: الوقت الماضي
        """
        if isinstance(datetime_obj, str):
            try:
                datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
            except ValueError:
                return "تاريخ غير معروف"
        
        now = datetime.now()
        diff = now - datetime_obj
        
        if diff.days > 365:
            years = diff.days // 365
            return f"قبل {years} سنة"
        elif diff.days > 30:
            months = diff.days // 30
            return f"قبل {months} شهر"
        elif diff.days > 0:
            return f"قبل {diff.days} يوم"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"قبل {hours} ساعة"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"قبل {minutes} دقيقة"
        else:
            return "الآن"
    
    @staticmethod
    def get_client_ip():
        """
        الحصول على عنوان IP الخاص بالعميل
        
        Returns:
            str: عنوان IP
        """
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr
    
    @staticmethod
    def get_browser_info():
        """
        الحصول على معلومات المتصفح
        
        Returns:
            dict: معلومات المتصفح
        """
        user_agent = request.headers.get('User-Agent', '')
        
        info = {
            'user_agent': user_agent,
            'is_mobile': any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone']),
            'is_tablet': 'tablet' in user_agent.lower(),
            'is_desktop': not any(term in user_agent.lower() for term in ['mobile', 'tablet', 'android', 'iphone'])
        }
        
        return info
    
    @staticmethod
    def save_uploaded_file(file, upload_folder, allowed_extensions=None):
        """
        حفظ ملف تم تحميله
        
        Args:
            file: كائن الملف
            upload_folder: مجلد التحميل
            allowed_extensions: الامتدادات المسموحة
        
        Returns:
            tuple: (مسار الملف, اسم الملف) أو (None, رسالة الخطأ)
        """
        if not file:
            return None, "لم يتم تحميل ملف"
        
        filename = file.filename
        
        # التحقق من الامتداد
        if allowed_extensions:
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in allowed_extensions:
                return None, f"امتداد الملف غير مسموح. الامتدادات المسموحة: {', '.join(allowed_extensions)}"
        
        # إنشاء اسم فريد للملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_str = Helpers.generate_random_string(6)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}_{random_str}{ext}"
        
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(upload_folder, exist_ok=True)
        
        # حفظ الملف
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return file_path, unique_filename
    
    @staticmethod
    def export_to_excel(data, filename=None):
        """
        تصدير البيانات إلى Excel
        
        Args:
            data: البيانات (قائمة من القواميس)
            filename: اسم الملف (اختياري)
        
        Returns:
            BytesIO: كائن بايتس يحتوي على ملف Excel
        """
        if not data:
            return None
        
        df = pd.DataFrame(data)
        
        # إنشاء ملف Excel في الذاكرة
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='بيانات', index=False)
        
        output.seek(0)
        
        if filename and not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        return output, filename
    
    @staticmethod
    def export_to_json(data, filename=None):
        """
        تصدير البيانات إلى JSON
        
        Args:
            data: البيانات
            filename: اسم الملف (اختياري)
        
        Returns:
            BytesIO: كائن بايتس يحتوي على ملف JSON
        """
        json_data = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        
        mem = io.BytesIO()
        mem.write(json_data.encode('utf-8'))
        mem.seek(0)
        
        if filename and not filename.endswith('.json'):
            filename += '.json'
        
        return mem, filename
    
    @staticmethod
    def import_from_json(file):
        """
        استيراد البيانات من ملف JSON
        
        Args:
            file: كائن الملف
        
        Returns:
            dict: البيانات المستوردة
        """
        try:
            data = json.loads(file.read().decode('utf-8'))
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"خطأ في تحليل ملف JSON: {e}")
    
    @staticmethod
    def calculate_statistics(data, field, stat_type='average'):
        """
        حساب الإحصائيات
        
        Args:
            data: البيانات
            field: الحقل المطلوب
            stat_type: نوع الإحصائية ('average', 'sum', 'min', 'max', 'count')
        
        Returns:
            float or int: قيمة الإحصائية
        """
        if not data:
            return 0
        
        values = []
        for item in data:
            if field in item and item[field] is not None:
                try:
                    values.append(float(item[field]))
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return 0
        
        if stat_type == 'average':
            return sum(values) / len(values)
        elif stat_type == 'sum':
            return sum(values)
        elif stat_type == 'min':
            return min(values)
        elif stat_type == 'max':
            return max(values)
        elif stat_type == 'count':
            return len(values)
        else:
            return 0
    
    @staticmethod
    def group_by(data, field):
        """
        تجميع البيانات حسب حقل
        
        Args:
            data: البيانات
            field: الحقل للتجميع
        
        Returns:
            dict: البيانات المجمعة
        """
        grouped = {}
        
        for item in data:
            key = item.get(field, 'غير محدد')
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        
        return grouped
    
    @staticmethod
    def filter_by_date(data, date_field, start_date=None, end_date=None):
        """
        تصفية البيانات حسب التاريخ
        
        Args:
            data: البيانات
            date_field: حقل التاريخ
            start_date: تاريخ البدء (اختياري)
            end_date: تاريخ الانتهاء (اختياري)
        
        Returns:
            list: البيانات المصفاة
        """
        filtered = []
        
        for item in data:
            date_str = item.get(date_field)
            if not date_str:
                continue
            
            try:
                item_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue
                
                filtered.append(item)
            except ValueError:
                continue
        
        return filtered
    
    @staticmethod
    def get_period_dates(period='month'):
        """
        الحصول على تواريخ فترة محددة
        
        Args:
            period: الفترة ('today', 'week', 'month', 'year')
        
        Returns:
            tuple: (تاريخ البدء, تاريخ الانتهاء)
        """
        today = date.today()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            # الحصول على آخر يوم في الشهر
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = today
            end_date = today
        
        return start_date, end_date

def get_current_user():
    """
    الحصول على بيانات المستخدم الحالي
    
    Returns:
        dict: بيانات المستخدم أو None
    """
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_full_name = session.get('user_full_name')
    user_role = session.get('user_role')
    
    if user_id:
        return {
            'id': user_id,
            'username': user_name,
            'full_name': user_full_name,
            'role': user_role
        }
    
    return None

def has_permission(required_role):
    """
    التحقق من صلاحية المستخدم
    
    Args:
        required_role: الدور المطلوب أو قائمة الأدوار
    
    Returns:
        bool: صحيح إذا كان المستخدم لديه الصلاحية
    """
    user = get_current_user()
    if not user:
        return False
    
    if isinstance(required_role, list):
        return user['role'] in required_role
    else:
        return user['role'] == required_role

def get_role_display(role):
    """
    الحصول على اسم الدور بالعربية
    
    Args:
        role: دور المستخدم
    
    Returns:
        str: اسم الدور بالعربية
    """
    roles = {
        'admin': 'مدير النظام',
        'doctor': 'طبيب',
        'nurse': 'ممرض/ممرضة',
        'view': 'مشاهد فقط'
    }
    return roles.get(role, role)

def get_status_display(status):
    """
    الحصول على اسم الحالة بالعربية
    
    Args:
        status: الحالة
    
    Returns:
        str: اسم الحالة بالعربية
    """
    statuses = {
        'نشط': 'نشط',
        'غير نشط': 'غير نشط',
        'بانتظار الفحص': 'بانتظار الفحص',
        'مكتمل': 'مكتمل',
        'مجدول': 'مجدول',
        'ملغى': 'ملغى',
        'active': 'نشط',
        'inactive': 'غير نشط',
        'pending': 'بانتظار الفحص',
        'completed': 'مكتمل',
        'scheduled': 'مجدول',
        'cancelled': 'ملغى'
    }
    return statuses.get(status, status)

def get_gender_display(gender):
    """
    الحصول على الجنس بالعربية
    
    Args:
        gender: الجنس
    
    Returns:
        str: الجنس بالعربية
    """
    genders = {
        'ذكر': 'ذكر',
        'أنثى': 'أنثى',
        'male': 'ذكر',
        'female': 'أنثى'
    }
    return genders.get(gender, gender)

def format_phone_number(phone):
    """
    تنسيق رقم الهاتف
    
    Args:
        phone: رقم الهاتف
    
    Returns:
        str: رقم الهاتف المنسق
    """
    if not phone:
        return ""
    
    # إزالة جميع الأحرف غير الرقمية
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 10 and digits.startswith('05'):
        return f"+966 {digits[1:4]} {digits[4:7]} {digits[7:]}"
    elif len(digits) == 12 and digits.startswith('966'):
        return f"+{digits[0:3]} {digits[3:6]} {digits[6:9]} {digits[9:]}"
    else:
        return phone

# Wrapper functions for top-level imports
def get_arabic_date(date_obj=None):
    """Wrapper for Helpers.get_arabic_date"""
    return Helpers.get_arabic_date(date_obj)
