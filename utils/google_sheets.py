"""
تكامل مع Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
import json
import os
from flask import current_app

class GoogleSheetsManager:
    """مدير Google Sheets"""
    
    def __init__(self, credentials_file=None, sheet_id=None):
        """
        تهيئة مدير Google Sheets
        
        Args:
            credentials_file: مسار ملف الاعتماد
            sheet_id: معرف جدول Google Sheets
        """
        self.credentials_file = credentials_file or 'credentials.json'
        self.sheet_id = sheet_id
        self.client = None
        self.authenticated = False
        
    def authenticate(self):
        """
        المصادقة مع Google Sheets API
        
        Returns:
            bool: صحيح إذا تمت المصادقة بنجاح
        """
        try:
            # تحديد النطاقات المطلوبة
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            creds = None
            
            # التحقق من وجود ملف الاعتماد
            if not os.path.exists(self.credentials_file):
                print(f"ملف الاعتماد غير موجود: {self.credentials_file}")
                return False
            
            # محاولة تحميل الاعتماد من ملف token
            token_file = 'token.json'
            if os.path.exists(token_file):
                try:
                    creds = OAuthCredentials.from_authorized_user_file(token_file, SCOPES)
                except Exception as e:
                    print(f"خطأ في تحميل token: {e}")
            
            # إذا لم تكن هناك بيانات اعتماد صالحة، اطلب المصادقة
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # حفظ الاعتماد للمرة القادمة
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # إنشاء العميل
            self.client = gspread.authorize(creds)
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"خطأ في المصادقة: {e}")
            self.authenticated = False
            return False
    
    def get_spreadsheet(self):
        """
        الحصول على جدول البيانات
        
        Returns:
            gspread.Spreadsheet: كائن جدول البيانات أو None
        """
        if not self.authenticated or not self.client or not self.sheet_id:
            return None
        
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            return spreadsheet
        except Exception as e:
            print(f"خطأ في الحصول على جدول البيانات: {e}")
            return None
    
    def get_worksheet(self, title='المرضى'):
        """
        الحصول على ورقة عمل
        
        Args:
            title: عنوان ورقة العمل
        
        Returns:
            gspread.Worksheet: كائن ورقة العمل أو None
        """
        spreadsheet = self.get_spreadsheet()
        if not spreadsheet:
            return None
        
        try:
            worksheet = spreadsheet.worksheet(title)
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # إنشاء ورقة عمل جديدة إذا لم تكن موجودة
            try:
                worksheet = spreadsheet.add_worksheet(title=title, rows=100, cols=20)
                return worksheet
            except Exception as e:
                print(f"خطأ في إنشاء ورقة العمل: {e}")
                return None
        except Exception as e:
            print(f"خطأ في الحصول على ورقة العمل: {e}")
            return None
    
    def export_patients(self, patients_data):
        """
        تصدير بيانات المرضى إلى Google Sheets
        
        Args:
            patients_data: قائمة بيانات المرضى
        
        Returns:
            bool: صحيح إذا تم التصدير بنجاح
        """
        worksheet = self.get_worksheet('المرضى')
        if not worksheet:
            return False
        
        try:
            # تحضير البيانات
            data = []
            headers = ['رقم الملف', 'الاسم', 'العمر', 'الجنس', 'رقم الهاتف', 
                      'العنوان', 'التشخيص', 'الحالة', 'تاريخ التسجيل', 'تاريخ التحديث']
            data.append(headers)
            
            for patient in patients_data:
                row = [
                    patient.get('file_number', ''),
                    patient.get('name', ''),
                    patient.get('age', ''),
                    patient.get('gender', ''),
                    patient.get('phone', ''),
                    patient.get('address', ''),
                    patient.get('diagnosis', ''),
                    patient.get('status', ''),
                    patient.get('created_at', ''),
                    patient.get('updated_at', '')
                ]
                data.append(row)
            
            # مسح الورقة القديمة وكتابة البيانات الجديدة
            worksheet.clear()
            worksheet.update('A1', data)
            
            # تنسيق الرأس
            header_format = {
                "backgroundColor": {
                    "red": 0.2,
                    "green": 0.4,
                    "blue": 0.8
                },
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    },
                    "bold": True
                }
            }
            
            worksheet.format('A1:J1', header_format)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تصدير بيانات المرضى: {e}")
            return False
    
    def export_users(self, users_data):
        """
        تصدير بيانات المستخدمين إلى Google Sheets
        
        Args:
            users_data: قائمة بيانات المستخدمين
        
        Returns:
            bool: صحيح إذا تم التصدير بنجاح
        """
        worksheet = self.get_worksheet('المستخدمون')
        if not worksheet:
            return False
        
        try:
            # تحضير البيانات
            data = []
            headers = ['الاسم الكامل', 'اسم المستخدم', 'البريد الإلكتروني', 
                      'رقم الهاتف', 'الدور', 'الحالة', 'تاريخ الإنشاء', 'تاريخ التحديث']
            data.append(headers)
            
            for user in users_data:
                # عدم تصدير كلمة المرور لأسباب أمنية
                row = [
                    user.get('full_name', ''),
                    user.get('username', ''),
                    user.get('email', ''),
                    user.get('phone', ''),
                    user.get('role', ''),
                    user.get('status', ''),
                    user.get('created_at', ''),
                    user.get('updated_at', '')
                ]
                data.append(row)
            
            # مسح الورقة القديمة وكتابة البيانات الجديدة
            worksheet.clear()
            worksheet.update('A1', data)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تصدير بيانات المستخدمين: {e}")
            return False
    
    def import_patients(self):
        """
        استيراد بيانات المرضى من Google Sheets
        
        Returns:
            list: قائمة بيانات المرضى
        """
        worksheet = self.get_worksheet('المرضى')
        if not worksheet:
            return []
        
        try:
            # جلب جميع البيانات
            data = worksheet.get_all_records()
            
            patients = []
            for row in data:
                patient = {
                    'file_number': row.get('رقم الملف', ''),
                    'name': row.get('الاسم', ''),
                    'age': row.get('العمر', ''),
                    'gender': row.get('الجنس', ''),
                    'phone': row.get('رقم الهاتف', ''),
                    'address': row.get('العنوان', ''),
                    'diagnosis': row.get('التشخيص', ''),
                    'status': row.get('الحالة', 'نشط'),
                    'created_at': row.get('تاريخ التسجيل', datetime.now().isoformat()),
                    'updated_at': row.get('تاريخ التحديث', datetime.now().isoformat())
                }
                patients.append(patient)
            
            return patients
            
        except Exception as e:
            print(f"خطأ في استيراد بيانات المرضى: {e}")
            return []
    
    def import_users(self):
        """
        استيراد بيانات المستخدمين من Google Sheets
        
        Returns:
            list: قائمة بيانات المستخدمين
        """
        worksheet = self.get_worksheet('المستخدمون')
        if not worksheet:
            return []
        
        try:
            # جلب جميع البيانات
            data = worksheet.get_all_records()
            
            users = []
            for row in data:
                user = {
                    'full_name': row.get('الاسم الكامل', ''),
                    'username': row.get('اسم المستخدم', ''),
                    'email': row.get('البريد الإلكتروني', ''),
                    'phone': row.get('رقم الهاتف', ''),
                    'role': row.get('الدور', 'view'),
                    'status': row.get('الحالة', 'نشط'),
                    'created_at': row.get('تاريخ الإنشاء', datetime.now().isoformat()),
                    'updated_at': row.get('تاريخ التحديث', datetime.now().isoformat())
                }
                users.append(user)
            
            return users
            
        except Exception as e:
            print(f"خطأ في استيراد بيانات المستخدمين: {e}")
            return []
    
    def test_connection(self):
        """
        اختبار الاتصال بـ Google Sheets
        
        Returns:
            dict: نتيجة الاختبار
        """
        try:
            if not self.authenticate():
                return {
                    'success': False,
                    'message': 'فشل المصادقة مع Google Sheets API'
                }
            
            spreadsheet = self.get_spreadsheet()
            if not spreadsheet:
                return {
                    'success': False,
                    'message': 'فشل الوصول إلى جدول البيانات'
                }
            
            # محاولة قراءة أول ورقة عمل
            worksheets = spreadsheet.worksheets()
            
            return {
                'success': True,
                'message': f'تم الاتصال بنجاح. عدد أوراق العمل: {len(worksheets)}',
                'spreadsheet_title': spreadsheet.title,
                'worksheets': [ws.title for ws in worksheets]
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
    
    def sync_all_data(self, patients_data, users_data, medical_records_data=None, visits_data=None):
        """
        مزامنة جميع البيانات مع Google Sheets
        
        Args:
            patients_data: بيانات المرضى
            users_data: بيانات المستخدمين
            medical_records_data: بيانات السجلات الطبية (اختياري)
            visits_data: بيانات الزيارات (اختياري)
        
        Returns:
            dict: نتيجة المزامنة
        """
        results = {
            'success': True,
            'details': {}
        }
        
        try:
            # تصدير المرضى
            if patients_data:
                patients_result = self.export_patients(patients_data)
                results['details']['patients'] = {
                    'success': patients_result,
                    'count': len(patients_data)
                }
                if not patients_result:
                    results['success'] = False
            
            # تصدير المستخدمين
            if users_data:
                users_result = self.export_users(users_data)
                results['details']['users'] = {
                    'success': users_result,
                    'count': len(users_data)
                }
                if not users_result:
                    results['success'] = False
            
            # تصدير السجلات الطبية (إذا كانت متاحة)
            if medical_records_data:
                medical_result = self.export_medical_records(medical_records_data)
                results['details']['medical_records'] = {
                    'success': medical_result,
                    'count': len(medical_records_data)
                }
                if not medical_result:
                    results['success'] = False
            
            # تصدير الزيارات (إذا كانت متاحة)
            if visits_data:
                visits_result = self.export_visits(visits_data)
                results['details']['visits'] = {
                    'success': visits_result,
                    'count': len(visits_data)
                }
                if not visits_result:
                    results['success'] = False
            
            if results['success']:
                results['message'] = 'تمت المزامنة بنجاح'
            else:
                results['message'] = 'حدثت أخطاء أثناء المزامنة'
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في المزامنة: {str(e)}',
                'details': {}
            }
    
    def export_medical_records(self, medical_records_data):
        """
        تصدير بيانات السجلات الطبية إلى Google Sheets
        
        Args:
            medical_records_data: قائمة بيانات السجلات الطبية
        
        Returns:
            bool: صحيح إذا تم التصدير بنجاح
        """
        worksheet = self.get_worksheet('السجلات الطبية')
        if not worksheet:
            return False
        
        try:
            # تحضير البيانات
            data = []
            headers = ['رقم المريض', 'اسم المريض', 'التشخيص', 'العلاج', 
                      'ملاحظات', 'التاريخ', 'الطبيب المعالج', 'تاريخ الإنشاء']
            data.append(headers)
            
            for record in medical_records_data:
                row = [
                    record.get('patient_id', ''),
                    record.get('patient_name', ''),
                    record.get('diagnosis', ''),
                    record.get('treatment', ''),
                    record.get('notes', ''),
                    record.get('date', ''),
                    record.get('doctor_name', ''),
                    record.get('created_at', '')
                ]
                data.append(row)
            
            worksheet.clear()
            worksheet.update('A1', data)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تصدير السجلات الطبية: {e}")
            return False
    
    def export_visits(self, visits_data):
        """
        تصدير بيانات الزيارات إلى Google Sheets
        
        Args:
            visits_data: قائمة بيانات الزيارات
        
        Returns:
            bool: صحيح إذا تم التصدير بنجاح
        """
        worksheet = self.get_worksheet('الزيارات')
        if not worksheet:
            return False
        
        try:
            # تحضير البيانات
            data = []
            headers = ['رقم المريض', 'اسم المريض', 'التاريخ', 'الوقت', 
                      'الغرض', 'التشخيص', 'الوصفة', 'الحالة', 'الطبيب', 'تاريخ الإنشاء']
            data.append(headers)
            
            for visit in visits_data:
                row = [
                    visit.get('patient_id', ''),
                    visit.get('patient_name', ''),
                    visit.get('date', ''),
                    visit.get('time', ''),
                    visit.get('purpose', ''),
                    visit.get('diagnosis', ''),
                    visit.get('prescription', ''),
                    visit.get('status', ''),
                    visit.get('doctor_name', ''),
                    visit.get('created_at', '')
                ]
                data.append(row)
            
            worksheet.clear()
            worksheet.update('A1', data)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تصدير الزيارات: {e}")
            return False

def get_google_sheets_manager():
    """
    الحصول على مدير Google Sheets من إعدادات التطبيق
    
    Returns:
        GoogleSheetsManager: مدير Google Sheets أو None
    """
    from database.db_handler import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT script_url, sheet_id FROM settings WHERE id = 1')
    settings = cursor.fetchone()
    conn.close()
    
    if not settings or not settings['script_url']:
        return None
    
    # في هذا المثال، سنستخدم Google Sheets API مباشرة
    # للتبسيط، سنستخدم جدول افتراضي
    sheet_id = settings['sheet_id'] or '1_JvtLlgrN5GoNIIO7tP0eGsdd3sH9RXRLH7VlN8d9HM'
    
    manager = GoogleSheetsManager(
        credentials_file='credentials.json',
        sheet_id=sheet_id
    )
    
    return manager

def sync_with_google_sheets():
    """
    مزامنة البيانات مع Google Sheets
    
    Returns:
        dict: نتيجة المزامنة
    """
    from models.patient import Patient
    from models.user import User
    from models.medical_record import MedicalRecord
    from models.visit import Visit
    
    manager = get_google_sheets_manager()
    if not manager:
        return {
            'success': False,
            'message': 'لم يتم تكوين Google Sheets'
        }
    
    # جلب البيانات المحلية
    patients = Patient.get_all()
    users = User.get_all()
    medical_records = MedicalRecord.get_all()
    visits = Visit.get_all()
    
    # تحويل البيانات إلى قواميس
    patients_data = [p.to_dict() for p in patients]
    users_data = [u.to_dict() for u in users]
    medical_records_data = [mr.to_dict() for mr in medical_records]
    visits_data = [v.to_dict() for v in visits]
    
    # إضافة أسماء المرضى والأطباء للسجلات الطبية والزيارات
    for record in medical_records_data:
        record['patient_name'] = record.get('patient', {}).get('name', '') if isinstance(record.get('patient'), dict) else ''
        record['doctor_name'] = record.get('doctor', {}).get('full_name', '') if isinstance(record.get('doctor'), dict) else ''
    
    for visit in visits_data:
        visit['patient_name'] = visit.get('patient', {}).get('name', '') if isinstance(visit.get('patient'), dict) else ''
        visit['doctor_name'] = visit.get('doctor', {}).get('full_name', '') if isinstance(visit.get('doctor'), dict) else ''
    
    # المزامنة
    return manager.sync_all_data(
        patients_data=patients_data,
        users_data=users_data,
        medical_records_data=medical_records_data,
        visits_data=visits_data
    )