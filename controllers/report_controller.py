from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from database.db_handler import get_db_connection
from datetime import datetime, date, timedelta
import json
import pandas as pd
import io

report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # إحصائيات حسب الجنس
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN gender = 'ذكر' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN gender = 'أنثى' THEN 1 ELSE 0 END) as female
        FROM patients
    ''')
    gender_stats = cursor.fetchone()
    
    # إحصائيات حسب العمر
    cursor.execute('SELECT AVG(age) as average_age FROM patients')
    age_stats = cursor.fetchone()
    
    # عدد الزيارات هذا الشهر
    first_day = date.today().replace(day=1)
    cursor.execute('SELECT COUNT(*) FROM visits WHERE date >= ?', (first_day.isoformat(),))
    monthly_visits = cursor.fetchone()[0]
    
    # التشخيصات الشائعة
    cursor.execute('''
        SELECT diagnosis, COUNT(*) as count
        FROM patients 
        WHERE diagnosis IS NOT NULL AND diagnosis != ''
        GROUP BY diagnosis 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    common_diagnoses = cursor.fetchall()
    
    conn.close()
    
    return render_template('reports.html', 
                         reports={
                             'gender_stats': dict(gender_stats),
                             'age_stats': dict(age_stats),
                             'monthly_visits': monthly_visits,
                             'common_diagnoses': common_diagnoses
                         })

@report_bp.route('/generate')
def generate_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    report_type = request.args.get('type', 'patients')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if report_type == 'patients':
        query = '''
            SELECT file_number, name, age, gender, phone, diagnosis, 
                   status, created_at
            FROM patients
        '''
        params = []
        
        if from_date and to_date:
            query += ' WHERE created_at BETWEEN ? AND ?'
            params.extend([from_date, to_date])
        elif from_date:
            query += ' WHERE created_at >= ?'
            params.append(from_date)
        elif to_date:
            query += ' WHERE created_at <= ?'
            params.append(to_date)
        
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        
    elif report_type == 'visits':
        query = '''
            SELECT v.date, v.time, v.purpose, v.diagnosis, v.status,
                   p.name as patient_name, p.file_number,
                   u.full_name as doctor_name
            FROM visits v
            LEFT JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.doctor_id = u.id
        '''
        params = []
        
        if from_date and to_date:
            query += ' WHERE v.date BETWEEN ? AND ?'
            params.extend([from_date, to_date])
        elif from_date:
            query += ' WHERE v.date >= ?'
            params.append(from_date)
        elif to_date:
            query += ' WHERE v.date <= ?'
            params.append(to_date)
        
        query += ' ORDER BY v.date DESC, v.time DESC'
        cursor.execute(query, params)
    
    data = cursor.fetchall()
    conn.close()
    
    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data)
    
    # إنشاء تقرير HTML
    html_report = f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير {report_type}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .footer {{ margin-top: 30px; text-align: left; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>تقرير {report_type}</h1>
            <p>تاريخ الإنشاء: {date.today().isoformat()}</p>
            <p>الفترة: {from_date if from_date else 'البداية'} إلى {to_date if to_date else 'النهاية'}</p>
        </div>
        
        {df.to_html(index=False, classes='report-table')}
        
        <div class="footer">
            <p>نظام إدارة المستشفى - تم إنشاء التقرير تلقائياً</p>
        </div>
    </body>
    </html>
    '''
    
    return html_report

@report_bp.route('/export-excel')
def export_excel():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    report_type = request.args.get('type', 'patients')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if report_type == 'patients':
        query = '''
            SELECT file_number as "رقم الملف", name as "الاسم", age as "العمر", 
                   gender as "الجنس", phone as "الهاتف", diagnosis as "التشخيص", 
                   status as "الحالة", created_at as "تاريخ التسجيل"
            FROM patients
        '''
        params = []
        
        if from_date and to_date:
            query += ' WHERE created_at BETWEEN ? AND ?'
            params.extend([from_date, to_date])
        
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        
        filename = f"تقرير_المرضى_{date.today().isoformat()}.xlsx"
        
    elif report_type == 'visits':
        query = '''
            SELECT v.date as "التاريخ", v.time as "الوقت", v.purpose as "الغرض", 
                   v.diagnosis as "التشخيص", v.status as "الحالة",
                   p.name as "اسم المريض", p.file_number as "رقم الملف",
                   u.full_name as "الطبيب المعالج"
            FROM visits v
            LEFT JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.doctor_id = u.id
        '''
        params = []
        
        if from_date and to_date:
            query += ' WHERE v.date BETWEEN ? AND ?'
            params.extend([from_date, to_date])
        
        query += ' ORDER BY v.date DESC, v.time DESC'
        cursor.execute(query, params)
        
        filename = f"تقرير_الزيارات_{date.today().isoformat()}.xlsx"
    
    data = cursor.fetchall()
    conn.close()
    
    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data)
    
    # إنشاء ملف Excel في الذاكرة
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='تقرير', index=False)
    
    output.seek(0)
    
    return send_file(output, 
                     as_attachment=True, 
                     download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')