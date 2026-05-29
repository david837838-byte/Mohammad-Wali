"""
أدوات تصدير البيانات إلى Excel
"""

import pandas as pd
import io
from datetime import datetime
from flask import send_file

class ExcelExporter:
    """مصدر البيانات إلى Excel"""
    
    @staticmethod
    def export_patients(patients):
        """
        تصدير بيانات المرضى إلى Excel
        
        Args:
            patients: قائمة المرضى
        
        Returns:
            Flask response: استجابة مع ملف Excel
        """
        data = []
        for patient in patients:
            data.append({
                'رقم الملف': patient.file_number,
                'الاسم': patient.name,
                'العمر': patient.age,
                'الجنس': patient.get_gender_display(),
                'رقم الهاتف': patient.phone,
                'العنوان': patient.address,
                'التشخيص': patient.diagnosis or '',
                'الحالة': patient.status,
                'تاريخ التسجيل': patient.created_at
            })
        
        df = pd.DataFrame(data)
        
        # إنشاء ملف Excel في الذاكرة
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='المرضى', index=False)
        
        output.seek(0)
        filename = f"مرضى_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    @staticmethod
    def export_users(users):
        """
        تصدير بيانات المستخدمين إلى Excel
        
        Args:
            users: قائمة المستخدمين
        
        Returns:
            Flask response: استجابة مع ملف Excel
        """
        data = []
        for user in users:
            data.append({
                'الاسم الكامل': user.full_name,
                'اسم المستخدم': user.username,
                'البريد الإلكتروني': user.email or '',
                'رقم الهاتف': user.phone or '',
                'الدور': user.get_role_display(),
                'الحالة': user.status,
                'تاريخ الإنشاء': user.created_at
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='المستخدمون', index=False)
        
        output.seek(0)
        filename = f"مستخدمون_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    @staticmethod
    def export_medical_records(records):
        """
        تصدير بيانات السجلات الطبية إلى Excel
        
        Args:
            records: قائمة السجلات الطبية
        
        Returns:
            Flask response: استجابة مع ملف Excel
        """
        data = []
        for record in records:
            data.append({
                'اسم المريض': record.get_patient_name(),
                'رقم ملف المريض': record.patient.file_number if record.patient else '',
                'التشخيص': record.diagnosis or '',
                'العلاج': record.treatment or '',
                'ملاحظات': record.notes or '',
                'التاريخ': record.get_formatted_date(),
                'الطبيب المعالج': record.get_doctor_name()
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='السجلات الطبية', index=False)
        
        output.seek(0)
        filename = f"سجلات_طبية_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    @staticmethod
    def export_visits(visits):
        """
        تصدير بيانات الزيارات إلى Excel
        
        Args:
            visits: قائمة الزيارات
        
        Returns:
            Flask response: استجابة مع ملف Excel
        """
        data = []
        for visit in visits:
            data.append({
                'اسم المريض': visit.get_patient_name(),
                'رقم ملف المريض': visit.patient.file_number if visit.patient else '',
                'التاريخ': visit.get_formatted_date(),
                'الوقت': visit.time_str,
                'الغرض': visit.purpose or '',
                'التشخيص': visit.diagnosis or '',
                'الوصفة': visit.prescription or '',
                'الحالة': visit.status,
                'الطبيب المعالج': visit.get_doctor_name()
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='الزيارات', index=False)
        
        output.seek(0)
        filename = f"زيارات_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )