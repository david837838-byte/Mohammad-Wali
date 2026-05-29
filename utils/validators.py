"""
أدوات التحقق من صحة البيانات
"""

import re
from datetime import datetime
from flask import flash

class Validators:
    """فئة التحقق من صحة البيانات"""
    
    @staticmethod
    def validate_required(fields, field_names=None):
        """
        التحقق من وجود الحقول المطلوبة
        
        Args:
            fields: قاموس الحقول
            field_names: قائمة أسماء الحوامل المطلوبة (اختياري)
        
        Returns:
            tuple: (صحيح/خطأ, رسالة الخطأ)
        """
        if field_names is None:
            field_names = list(fields.keys())
        
        missing_fields = []
        for field in field_names:
            value = fields.get(field)
            if not value or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"الحقول التالية مطلوبة: {', '.join(missing_fields)}"
        
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """
        التحقق من صحة البريد الإلكتروني
        
        Args:
            email: البريد الإلكتروني
        
        Returns:
            bool: صحيح إذا كان البريد صالحاً
        """
        if not email:
            return True  # البريد اختياري
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """
        التحقق من صحة رقم الهاتف
        
        Args:
            phone: رقم الهاتف
        
        Returns:
            bool: صحيح إذا كان الهاتف صالحاً
        """
        if not phone:
            return False
        
        # نمط لرقم الهاتف السعودي
        pattern = r'^(05\d{8}|5\d{8}|\+9665\d{8})$'
        return re.match(pattern, phone.replace(' ', '')) is not None
    
    @staticmethod
    def validate_age(age):
        """
        التحقق من صحة العمر
        
        Args:
            age: العمر
        
        Returns:
            bool: صحيح إذا كان العمر صالحاً
        """
        try:
            age_int = int(age)
            return 0 <= age_int <= 150
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date(date_str, format='%Y-%m-%d'):
        """
        التحقق من صحة التاريخ
        
        Args:
            date_str: تاريخ كنص
            format: تنسيق التاريخ
        
        Returns:
            bool: صحيح إذا كان التاريخ صالحاً
        """
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_password(password):
        """
        التحقق من قوة كلمة المرور
        
        Args:
            password: كلمة المرور
        
        Returns:
            tuple: (صحيح/خطأ, رسالة الخطأ)
        """
        if len(password) < 6:
            return False, "كلمة المرور يجب أن تكون 6 أحرف على الأقل"
        
        if len(password) > 50:
            return False, "كلمة المرور طويلة جداً"
        
        return True, ""
    
    @staticmethod
    def validate_username(username):
        """
        التحقق من صحة اسم المستخدم
        
        Args:
            username: اسم المستخدم
        
        Returns:
            tuple: (صحيح/خطأ, رسالة الخطأ)
        """
        if len(username) < 3:
            return False, "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"
        
        if len(username) > 30:
            return False, "اسم المستخدم طويل جداً"
        
        pattern = r'^[a-zA-Z0-9_]+$'
        if not re.match(pattern, username):
            return False, "اسم المستخدم يجب أن يحتوي على أحرف إنجليزية وأرقام وشرطة سفلية فقط"
        
        return True, ""
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """
        التحقق من امتداد الملف
        
        Args:
            filename: اسم الملف
            allowed_extensions: قائمة الامتدادات المسموحة
        
        Returns:
            bool: صحيح إذا كان الامتداد مسموحاً
        """
        if not filename:
            return False
        
        ext = filename.rsplit('.', 1)[-1].lower()
        return ext in allowed_extensions
    
    @staticmethod
    def validate_file_size(file_size, max_size_mb):
        """
        التحقق من حجم الملف
        
        Args:
            file_size: حجم الملف بالبايت
            max_size_mb: الحد الأقصى بالميجابايت
        
        Returns:
            bool: صحيح إذا كان الحجم مقبولاً
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_gender(gender):
        """
        التحقق من صحة الجنس
        
        Args:
            gender: الجنس
        
        Returns:
            bool: صحيح إذا كان الجنس صالحاً
        """
        valid_genders = ['ذكر', 'أنثى', 'male', 'female']
        return gender in valid_genders
    
    @staticmethod
    def validate_role(role):
        """
        التحقق من صحة الدور
        
        Args:
            role: دور المستخدم
        
        Returns:
            bool: صحيح إذا كان الدور صالحاً
        """
        valid_roles = ['admin', 'doctor', 'nurse', 'view']
        return role in valid_roles
    
    @staticmethod
    def validate_status(status):
        """
        التحقق من صحة الحالة
        
        Args:
            status: حالة المريض أو المستخدم
        
        Returns:
            bool: صحيح إذا كانت الحالة صالحة
        """
        valid_statuses = ['نشط', 'غير نشط', 'بانتظار الفحص', 'مكتمل', 'مجدول', 'ملغى']
        return status in valid_statuses
    
    @staticmethod
    def validate_national_id(national_id):
        """
        التحقق من صحة الهوية الوطنية السعودية
        
        Args:
            national_id: رقم الهوية
        
        Returns:
            bool: صحيح إذا كانت الهوية صالحة
        """
        if not national_id or len(national_id) != 10:
            return False
        
        # التحقق من أن جميع الأحرف أرقام
        if not national_id.isdigit():
            return False
        
        # خوارزمية التحقق من رقم الهوية السعودية
        sum_digits = 0
        for i in range(10):
            digit = int(national_id[i])
            if i % 2 == 0:
                doubled = digit * 2
                sum_digits += doubled if doubled < 10 else doubled - 9
            else:
                sum_digits += digit
        
        return sum_digits % 10 == 0
    
    @staticmethod
    def validate_url(url):
        """
        التحقق من صحة الرابط
        
        Args:
            url: الرابط
        
        Returns:
            bool: صحيح إذا كان الرابط صالحاً
        """
        if not url:
            return True  # الرابط اختياري
        
        pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/\S*)?$'
        return re.match(pattern, url) is not None

def validate_patient_data(data):
    """
    التحقق من صحة بيانات المريض
    
    Args:
        data: بيانات المريض
    
    Returns:
        tuple: (صحيح/خطأ, رسالة الخطأ)
    """
    # التحقق من الحقول المطلوبة
    required_fields = ['name', 'age', 'gender', 'phone', 'address']
    valid, message = Validators.validate_required(data, required_fields)
    if not valid:
        return False, message
    
    # التحقق من العمر
    if not Validators.validate_age(data.get('age')):
        return False, "العمر غير صحيح (يجب أن يكون بين 0 و 150)"
    
    # التحقق من الجنس
    if not Validators.validate_gender(data.get('gender')):
        return False, "الجنس غير صحيح"
    
    # التحقق من الهاتف
    if not Validators.validate_phone(data.get('phone')):
        return False, "رقم الهاتف غير صحيح"
    
    # التحقق من الحالة إذا كانت موجودة
    status = data.get('status')
    if status and not Validators.validate_status(status):
        return False, "الحالة غير صحيحة"
    
    return True, ""

def validate_user_data(data, is_edit=False):
    """
    التحقق من صحة بيانات المستخدم
    
    Args:
        data: بيانات المستخدم
        is_edit: هل العملية تعديل؟
    
    Returns:
        tuple: (صحيح/خطأ, رسالة الخطأ)
    """
    # التحقق من الحقول المطلوبة
    required_fields = ['full_name', 'username', 'role']
    if not is_edit:
        required_fields.append('password')
    
    valid, message = Validators.validate_required(data, required_fields)
    if not valid:
        return False, message
    
    # التحقق من اسم المستخدم
    valid, message = Validators.validate_username(data.get('username'))
    if not valid:
        return False, message
    
    # التحقق من كلمة المرور (إذا كانت موجودة)
    password = data.get('password')
    if password and not is_edit:
        valid, message = Validators.validate_password(password)
        if not valid:
            return False, message
    
    # التحقق من البريد الإلكتروني
    email = data.get('email')
    if email and not Validators.validate_email(email):
        return False, "البريد الإلكتروني غير صحيح"
    
    # التحقق من الهاتف
    phone = data.get('phone')
    if phone and not Validators.validate_phone(phone):
        return False, "رقم الهاتف غير صحيح"
    
    # التحقق من الدور
    if not Validators.validate_role(data.get('role')):
        return False, "الدور غير صحيح"
    
    # التحقق من الحالة
    status = data.get('status')
    if status and not Validators.validate_status(status):
        return False, "الحالة غير صحيحة"
    
    return True, ""

def validate_medical_record_data(data):
    """
    التحقق من صحة بيانات السجل الطبي
    
    Args:
        data: بيانات السجل الطبي
    
    Returns:
        tuple: (صحيح/خطأ, رسالة الخطأ)
    """
    # التحقق من الحقول المطلوبة
    required_fields = ['patient_id']
    valid, message = Validators.validate_required(data, required_fields)
    if not valid:
        return False, message
    
    # التحقق من التاريخ
    date_str = data.get('date')
    if date_str and not Validators.validate_date(date_str):
        return False, "التاريخ غير صحيح"
    
    return True, ""

def validate_visit_data(data):
    """
    التحقق من صحة بيانات الزيارة
    
    Args:
        data: بيانات الزيارة
    
    Returns:
        tuple: (صحيح/خطأ, رسالة الخطأ)
    """
    # التحقق من الحقول المطلوبة
    required_fields = ['patient_id', 'date', 'time']
    valid, message = Validators.validate_required(data, required_fields)
    if not valid:
        return False, message
    
    # التحقق من التاريخ
    date_str = data.get('date')
    if not Validators.validate_date(date_str):
        return False, "التاريخ غير صحيح"
    
    # التحقق من الوقت
    time_str = data.get('time')
    if not Validators.validate_time(time_str):
        return False, "الوقت غير صحيح"
    
    # التحقق من الحالة
    status = data.get('status')
    if status and not Validators.validate_status(status):
        return False, "الحالة غير صحيحة"
    
    return True, ""

def validate_time(time_str):
    """
    التحقق من صحة الوقت
    
    Args:
        time_str: الوقت كنص
    
    Returns:
        bool: صحيح إذا كان الوقت صالحاً
    """
    if not time_str:
        return False
    
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return re.match(pattern, time_str) is not None

def flash_validation_errors(valid, message):
    """
    عرض رسائل التحقق من الصحة
    
    Args:
        valid: نتيجة التحقق
        message: رسالة الخطأ
    """
    if not valid:
        flash(message, 'error')
    return valid