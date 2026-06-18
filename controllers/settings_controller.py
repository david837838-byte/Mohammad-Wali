from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from database.db_handler import get_db_connection, init_db
from datetime import datetime, date
import json
import os
import io

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin', 'doctor']:
        flash('ليس لديك صلاحية للوصول إلى الإعدادات', 'error')
        return redirect(url_for('dashboard.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب إعدادات النظام
    cursor.execute('SELECT * FROM settings WHERE id = 1')
    settings = cursor.fetchone()
    
    if not settings:
        # إعدادات افتراضية
        settings = {
            'script_url': '',
            'sheet_id': '1_JvtLlgrN5GoNIIO7tP0eGsdd3sH9RXRLH7VlN8d9HM'
        }
    
    users = []
    if session.get('user_role') == 'admin':
        cursor.execute('''
            SELECT id, full_name, username, role, status
            FROM users
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
    
    conn.close()
    
    return render_template('settings.html', settings=settings, users=users)

@settings_bp.route('/update', methods=['POST'])
def update():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin', 'doctor']:
        flash('ليس لديك صلاحية لتعديل الإعدادات', 'error')
        return redirect(url_for('dashboard.index'))
    
    script_url = request.form.get('script_url', '')
    sheet_id = request.form.get('sheet_id', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من وجود إعدادات
    cursor.execute('SELECT COUNT(*) FROM settings WHERE id = 1')
    if cursor.fetchone()[0] > 0:
        cursor.execute('''
            UPDATE settings 
            SET script_url = ?, sheet_id = ?, updated_at = ?
            WHERE id = 1
        ''', (script_url, sheet_id, datetime.now().isoformat()))
    else:
        cursor.execute('''
            INSERT INTO settings (id, script_url, sheet_id, created_at, updated_at)
            VALUES (1, ?, ?, ?, ?)
        ''', (script_url, sheet_id, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    flash('تم حفظ الإعدادات بنجاح', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/clear-data', methods=['POST'])
def clear_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لحذف البيانات', 'error')
        return redirect(url_for('settings.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # حذف جميع البيانات (باستثناء المستخدمين والإعدادات)
    cursor.execute('DELETE FROM patients')
    cursor.execute('DELETE FROM medical_records')
    cursor.execute('DELETE FROM visits')
    
    conn.commit()
    conn.close()
    
    flash('تم حذف جميع البيانات بنجاح', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/export-data')
def export_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لتصدير البيانات', 'error')
        return redirect(url_for('settings.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب جميع البيانات
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    
    cursor.execute('SELECT * FROM medical_records')
    medical_records = cursor.fetchall()
    
    cursor.execute('SELECT * FROM visits')
    visits = cursor.fetchall()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    cursor.execute('SELECT * FROM settings')
    settings = cursor.fetchall()
    
    conn.close()
    
    # تحضير بيانات التصدير
    export_data = {
        'patients': [dict(p) for p in patients],
        'medical_records': [dict(mr) for mr in medical_records],
        'visits': [dict(v) for v in visits],
        'users': [dict(u) for u in users],
        'settings': [dict(s) for s in settings],
        'exported_at': datetime.now().isoformat(),
        'version': '1.0'
    }
    
    # إنشاء ملف JSON في الذاكرة
    json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
    mem = io.BytesIO()
    mem.write(json_data.encode('utf-8'))
    mem.seek(0)
    
    filename = f"hospital_data_export_{date.today().isoformat()}.json"
    
    flash('تم تصدير البيانات بنجاح', 'success')
    return send_file(mem, 
                     as_attachment=True, 
                     download_name=filename,
                     mimetype='application/json')

@settings_bp.route('/import-data', methods=['POST'])
def import_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لاستيراد البيانات', 'error')
        return redirect(url_for('settings.index'))
    
    if 'data_file' not in request.files:
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('settings.index'))
    
    file = request.files['data_file']
    
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('settings.index'))
    
    if not file.filename.endswith('.json'):
        flash('الملف يجب أن يكون بصيغة JSON', 'error')
        return redirect(url_for('settings.index'))
    
    try:
        # قراءة البيانات من الملف
        data = json.loads(file.read().decode('utf-8'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # استيراد البيانات
        if 'patients' in data:
            for patient in data['patients']:
                cursor.execute('''
                    INSERT OR REPLACE INTO patients 
                    (id, file_number, name, age, gender, phone, address, 
                     diagnosis, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient.get('id'), patient.get('file_number'), 
                    patient.get('name'), patient.get('age'), 
                    patient.get('gender'), patient.get('phone'), 
                    patient.get('address'), patient.get('diagnosis'), 
                    patient.get('status'), patient.get('created_at'), 
                    patient.get('updated_at', datetime.now().isoformat())
                ))
        
        if 'users' in data:
            for user in data['users']:
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (id, full_name, username, password, email, phone, 
                     role, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.get('id'), user.get('full_name'), 
                    user.get('username'), user.get('password'), 
                    user.get('email'), user.get('phone'), 
                    user.get('role'), user.get('status'), 
                    user.get('created_at'), user.get('updated_at', datetime.now().isoformat())
                ))
        
        conn.commit()
        conn.close()
        
        flash('تم استيراد البيانات بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في استيراد البيانات: {str(e)}', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/api/test-google-sheets')
def test_google_sheets():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    # هذه دالة بسيطة لاختبار الاتصال
    # في التطبيق الحقيقي، ستتصل بـ Google Sheets API
    
    return jsonify({
        'message': 'طلب اختبار الاتصال تم إرساله',
        'instructions': 'تحقق من وحدة التحكم في المتصفح للتفاصيل'
    })

@settings_bp.route('/api/refresh-google-sheets')
def refresh_google_sheets():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    # هذه دالة لمحاكاة جلب البيانات من Google Sheets
    # في التطبيق الحقيقي، ستجلب البيانات من Google Sheets API
    
    return jsonify({
        'success': True,
        'message': 'تم تحديث البيانات من Google Sheets بنجاح',
        'data_updated': datetime.now().isoformat()
    })