from flask import Flask, render_template, session, redirect, url_for, flash, jsonify, request, send_file
from flask_session import Session
from datetime import datetime, date, timedelta
import json
import os
import io
import pandas as pd

from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.patient_controller import patient_bp
from controllers.user_controller import user_bp
from controllers.settings_controller import settings_bp
from controllers.medical_controller import medical_bp
from controllers.visit_controller import visit_bp
from controllers.report_controller import report_bp
from database.db_handler import init_db, get_db_connection, seed_sample_data

from models.patient import Patient
from models.user import User
from models.medical_record import MedicalRecord
from models.visit import Visit
from utils.validators import validate_patient_data, validate_user_data
from utils.helpers import get_arabic_date, get_current_user, has_permission
from utils.google_sheets import get_google_sheets_manager, sync_with_google_sheets
from utils.excel_exporter import ExcelExporter

app = Flask(__name__)

# إعدادات التطبيق
app.config['SECRET_KEY'] = 'hospital-management-system-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['DATABASE'] = 'hospital.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# إنشاء مجلد التحميل إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

Session(app)

# تسجيل Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(user_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(medical_bp)
app.register_blueprint(visit_bp)
app.register_blueprint(report_bp)

# فلاتر قالب Jinja2
@app.template_filter('date_format')
def date_format(value, format='%Y-%m-%d'):
    if not value:
        return ''
    if isinstance(value, str):
        try:
            if 'T' in value:
                value = datetime.strptime(value.split('T')[0], '%Y-%m-%d')
            else:
                value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    elif isinstance(value, date):
        return value.strftime(format)
    return value

@app.template_filter('role_display')
def role_display(role):
    roles = {
        'admin': 'مدير النظام',
        'doctor': 'طبيب',
        'nurse': 'ممرض/ممرضة',
        'view': 'مشاهد فقط'
    }
    return roles.get(role, role)

@app.template_filter('status_class')
def status_class(status):
    classes = {
        'نشط': 'status-active',
        'بانتظار الفحص': 'status-pending',
        'غير نشط': 'status-inactive',
        'مكتمل': 'status-active',
        'مجدول': 'status-pending',
        'ملغى': 'status-inactive'
    }
    return classes.get(status, '')

@app.template_filter('role_class')
def role_class(role):
    classes = {
        'admin': 'role-admin',
        'doctor': 'role-doctor',
        'nurse': 'role-nurse',
        'view': 'role-view'
    }
    return classes.get(role, '')

@app.template_filter('gender_display')
def gender_display(gender):
    genders = {
        'ذكر': 'ذكر',
        'أنثى': 'أنثى',
        'male': 'ذكر',
        'female': 'أنثى'
    }
    return genders.get(gender, gender)

@app.template_filter('format_phone')
def format_phone(phone):
    """تنسيق رقم الهاتف"""
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

# إضافة المتغيرات العامة إلى جميع القوالب
@app.context_processor
def inject_user():
    user_info = {}
    if 'user_id' in session:
        user_info = {
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name', ''),
            'user_role': session.get('user_role', 'view'),
            'user_full_name': session.get('user_full_name', '')
        }
        
        # إضافة التاريخ العربي الحالي
        user_info['arabic_date'] = get_arabic_date()
        
        # إضافة البيانات الأساسية للقوائم المنسدلة
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # المرضى للقوائم المنسدلة
        cursor.execute('SELECT id, name, file_number FROM patients ORDER BY name')
        user_info['patients_list'] = cursor.fetchall()
        
        # المستخدمون (الأطباء) للقوائم المنسدلة
        cursor.execute("SELECT id, full_name FROM users WHERE role = 'doctor' AND status = 'نشط' ORDER BY full_name")
        user_info['doctors_list'] = cursor.fetchall()
        
        conn.close()
    
    return dict(current_user=user_info)

# صفحة رئيسية
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

# API لجلب الإحصائيات
@app.route('/api/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # عدد المرضى
    cursor.execute('SELECT COUNT(*) FROM patients')
    total_patients = cursor.fetchone()[0]
    
    # عدد الأطباء
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor' AND status = 'نشط'")
    total_doctors = cursor.fetchone()[0]
    
    # عدد المستخدمين
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # عدد الزيارات اليوم
    today = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) FROM visits WHERE date = ?', (today,))
    today_visits = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_users': total_users,
        'today_visits': today_visits
    })

# API لجلب الزيارات القادمة
@app.route('/api/upcoming-visits')
def get_upcoming_visits():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    today = date.today().isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.*, p.name as patient_name, p.file_number
        FROM visits v
        LEFT JOIN patients p ON v.patient_id = p.id
        WHERE v.date >= ? AND v.date <= ? AND v.status = 'مجدول'
        ORDER BY v.date, v.time
        LIMIT 10
    ''', (today, next_week))
    
    visits = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(visit) for visit in visits])

# API للبحث عن المرضى
@app.route('/api/search-patients')
def search_patients():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if query:
        cursor.execute('''
            SELECT id, file_number, name, age, phone
            FROM patients 
            WHERE name LIKE ? OR file_number LIKE ? OR phone LIKE ?
            ORDER BY name
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        cursor.execute('''
            SELECT id, file_number, name, age, phone
            FROM patients 
            ORDER BY name
            LIMIT 10
        ''')
    
    patients = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(patient) for patient in patients])

# API للبحث عن المستخدمين
@app.route('/api/search-users')
def search_users():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    if not has_permission('admin'):
        return jsonify({'error': 'ليس لديك صلاحية'}), 403
    
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if query:
        cursor.execute('''
            SELECT id, full_name, username, role
            FROM users 
            WHERE full_name LIKE ? OR username LIKE ?
            ORDER BY full_name
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%'))
    else:
        cursor.execute('''
            SELECT id, full_name, username, role
            FROM users 
            ORDER BY full_name
            LIMIT 10
        ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(user) for user in users])

# API لمزامنة Google Sheets
@app.route('/api/sync-google-sheets', methods=['POST'])
def sync_google_sheets():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    if not has_permission(['admin', 'doctor']):
        return jsonify({'error': 'ليس لديك صلاحية'}), 403
    
    try:
        result = sync_with_google_sheets()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في المزامنة: {str(e)}'
        })

# API لاختبار اتصال Google Sheets
@app.route('/api/test-google-sheets')
def test_google_sheets():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    if not has_permission(['admin', 'doctor']):
        return jsonify({'error': 'ليس لديك صلاحية'}), 403
    
    manager = get_google_sheets_manager()
    if not manager:
        return jsonify({
            'success': False,
            'message': 'لم يتم تكوين Google Sheets'
        })
    
    result = manager.test_connection()
    return jsonify(result)

# API لجلب إحصائيات متقدمة
@app.route('/api/advanced-stats')
def get_advanced_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # إحصائيات المرضى حسب الجنس
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN gender = 'ذكر' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN gender = 'أنثى' THEN 1 ELSE 0 END) as female
        FROM patients
    ''')
    gender_stats = cursor.fetchone()
    
    # إحصائيات المرضى حسب العمر
    cursor.execute('''
        SELECT 
            AVG(age) as average_age,
            MIN(age) as min_age,
            MAX(age) as max_age
        FROM patients
    ''')
    age_stats = cursor.fetchone()
    
    # إحصائيات المرضى حسب الحالة
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM patients
        GROUP BY status
    ''')
    status_stats = cursor.fetchall()
    
    # إحصائيات الزيارات
    cursor.execute('''
        SELECT 
            COUNT(*) as total_visits,
            SUM(CASE WHEN status = 'مكتمل' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'مجدول' THEN 1 ELSE 0 END) as scheduled,
            SUM(CASE WHEN status = 'ملغى' THEN 1 ELSE 0 END) as cancelled
        FROM visits
    ''')
    visit_stats = cursor.fetchone()
    
    # الزيارات في آخر 7 أيام
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    cursor.execute('''
        SELECT date, COUNT(*) as count
        FROM visits
        WHERE date >= ?
        GROUP BY date
        ORDER BY date
    ''', (seven_days_ago,))
    last_7_days_visits = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'gender_stats': dict(gender_stats),
        'age_stats': dict(age_stats),
        'status_stats': [dict(row) for row in status_stats],
        'visit_stats': dict(visit_stats),
        'last_7_days_visits': [dict(row) for row in last_7_days_visits]
    })

# API لتصدير البيانات إلى Excel
@app.route('/api/export-data/<data_type>')
def export_data(data_type):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if not has_permission(['admin', 'doctor']):
        flash('ليس لديك صلاحية لتصدير البيانات', 'error')
        return redirect(url_for('dashboard.index'))
    
    if data_type == 'patients':
        patients = Patient.get_all()
        return ExcelExporter.export_patients(patients)
    
    elif data_type == 'users' and has_permission('admin'):
        users = User.get_all()
        return ExcelExporter.export_users(users)
    
    elif data_type == 'medical_records':
        records = MedicalRecord.get_all()
        return ExcelExporter.export_medical_records(records)
    
    elif data_type == 'visits':
        visits = Visit.get_all()
        return ExcelExporter.export_visits(visits)
    
    else:
        flash('نوع البيانات غير صحيح', 'error')
        return redirect(url_for('dashboard.index'))

# API لتصدير تقرير مخصص
@app.route('/api/export-custom-report', methods=['POST'])
def export_custom_report():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    if not has_permission(['admin', 'doctor']):
        return jsonify({'error': 'ليس لديك صلاحية'}), 403
    
    data = request.json
    report_type = data.get('type')
    filters = data.get('filters', {})
    
    try:
        if report_type == 'patients':
            patients = Patient.get_all()
            
            # تطبيق الفلاتر
            if filters.get('start_date') and filters.get('end_date'):
                start_date = filters['start_date']
                end_date = filters['end_date']
                filtered_patients = []
                for patient in patients:
                    if start_date <= patient.created_at <= end_date:
                        filtered_patients.append(patient)
                patients = filtered_patients
            
            if filters.get('status'):
                patients = [p for p in patients if p.status == filters['status']]
            
            return ExcelExporter.export_patients(patients)
        
        elif report_type == 'visits':
            visits = Visit.get_all()
            
            # تطبيق الفلاتر
            if filters.get('start_date') and filters.get('end_date'):
                start_date = filters['start_date']
                end_date = filters['end_date']
                filtered_visits = []
                for visit in visits:
                    if start_date <= visit.date <= end_date:
                        filtered_visits.append(visit)
                visits = filtered_visits
            
            if filters.get('status'):
                visits = [v for v in visits if v.status == filters['status']]
            
            return ExcelExporter.export_visits(visits)
        
        else:
            return jsonify({'error': 'نوع التقرير غير مدعوم'}), 400
    
    except Exception as e:
        return jsonify({'error': f'خطأ في إنشاء التقرير: {str(e)}'}), 500

# صفحة البروفايل الشخصي
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    # جمع البيانات
    full_name = request.form.get('full_name', user.full_name)
    email = request.form.get('email', user.email)
    phone = request.form.get('phone', user.phone)
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # التحقق من كلمة المرور الحالية إذا أراد تغييرها
    if new_password:
        if not current_password:
            flash('يرجى إدخال كلمة المرور الحالية', 'error')
            return redirect(url_for('profile'))
        
        if user.password != current_password:
            flash('كلمة المرور الحالية غير صحيحة', 'error')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('كلمة المرور الجديدة غير متطابقة', 'error')
            return redirect(url_for('profile'))
        
        if len(new_password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return redirect(url_for('profile'))
        
        user.password = new_password
    
    # تحديث البيانات
    user.full_name = full_name
    user.email = email
    user.phone = phone
    
    # حفظ التغييرات
    user.save()
    
    # تحديث الجلسة
    session['user_full_name'] = user.full_name
    
    flash('تم تحديث البروفايل بنجاح', 'success')
    return redirect(url_for('profile'))

# صفحة حول النظام
@app.route('/about')
def about():
    return render_template('about.html')

# صفحة المساعدة
@app.route('/help')
def help_page():
    return render_template('help.html')

# API للحصول على إشعارات النظام
@app.route('/api/notifications')
def get_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    user_role = session.get('user_role', 'view')
    notifications = []
    
    # إشعارات للمديرين والأطباء
    if user_role in ['admin', 'doctor']:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # المرضى الذين ينتظرون الفحص
        cursor.execute("SELECT COUNT(*) FROM patients WHERE status = 'بانتظار الفحص'")
        pending_patients = cursor.fetchone()[0]
        
        if pending_patients > 0:
            notifications.append({
                'id': 1,
                'title': 'مرضى بانتظار الفحص',
                'message': f'هناك {pending_patients} مريض بانتظار الفحص',
                'type': 'warning',
                'link': '/patients'
            })
        
        # الزيارات المجدولة اليوم
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM visits WHERE date = ? AND status = 'مجدول'", (today,))
        today_visits = cursor.fetchone()[0]
        
        if today_visits > 0:
            notifications.append({
                'id': 2,
                'title': 'زيارات اليوم',
                'message': f'لديك {today_visits} زيارة مجدولة اليوم',
                'type': 'info',
                'link': '/visits'
            })
        
        # السجلات الطبية غير المكتملة
        cursor.execute('''
            SELECT COUNT(*) FROM medical_records 
            WHERE diagnosis IS NULL OR diagnosis = ''
        ''')
        incomplete_records = cursor.fetchone()[0]
        
        if incomplete_records > 0:
            notifications.append({
                'id': 3,
                'title': 'سجلات طبية غير مكتملة',
                'message': f'هناك {incomplete_records} سجل طبي غير مكتمل',
                'type': 'warning',
                'link': '/medical'
            })
        
        conn.close()
    
    # إشعارات خاصة بالمديرين فقط
    if user_role == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # المستخدمون غير النشطين
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'غير نشط'")
        inactive_users = cursor.fetchone()[0]
        
        if inactive_users > 0:
            notifications.append({
                'id': 4,
                'title': 'مستخدمون غير نشطين',
                'message': f'هناك {inactive_users} مستخدم غير نشط',
                'type': 'error',
                'link': '/users'
            })
        
        conn.close()
    
    return jsonify(notifications)

# معالج الأخطاء
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# تهيئة قاعدة البيانات عند بدء التشغيل
def initialize():
    init_db()
    seed_sample_data()
    
    # إضافة مستخدم مسؤول افتراضي إذا لم يكن موجوداً
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (full_name, username, password, email, phone, role, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('مدير النظام', 'admin', 'admin123', 'admin@hospital.com', '0512345678', 'admin', 'نشط', date.today().isoformat()))
        conn.commit()
    
    conn.close()

if __name__ == '__main__':
    initialize()
    app.run(debug=True, host='0.0.0.0', port=5000)