from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_handler import get_db_connection
from datetime import datetime, date
import json

patient_bp = Blueprint('patient', __name__, url_prefix='/patients')

@patient_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, file_number, name, age, gender, phone, address, 
               diagnosis, status, created_at
        FROM patients 
        ORDER BY created_at DESC
    ''')
    patients = cursor.fetchall()
    
    conn.close()
    
    return render_template('patients.html', patients=patients)

@patient_bp.route('/add')
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') == 'view':
        flash('ليس لديك صلاحية لإضافة مرضى', 'error')
        return redirect(url_for('patient.index'))
    
    return render_template('patient_form.html')

@patient_bp.route('/edit/<int:id>')
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') == 'view':
        flash('ليس لديك صلاحية لتعديل بيانات المرضى', 'error')
        return redirect(url_for('patient.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, file_number, name, age, gender, phone, address, 
               diagnosis, status, created_at
        FROM patients 
        WHERE id = ?
    ''', (id,))
    
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        flash('المريض غير موجود', 'error')
        return redirect(url_for('patient.index'))
    
    return render_template('patient_form.html', patient=patient)

@patient_bp.route('/view/<int:id>')
def view(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, file_number, name, age, gender, phone, address, 
               diagnosis, status, created_at
        FROM patients 
        WHERE id = ?
    ''', (id,))
    
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        flash('المريض غير موجود', 'error')
        return redirect(url_for('patient.index'))
    
    return render_template('patient_view.html', patient=patient)

@patient_bp.route('/save', methods=['POST'])
def save():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') == 'view':
        flash('ليس لديك صلاحية لإدارة المرضى', 'error')
        return redirect(url_for('patient.index'))
    
    patient_id = request.form.get('patient_id')
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    phone = request.form.get('phone')
    address = request.form.get('address')
    diagnosis = request.form.get('diagnosis', '')
    status = request.form.get('status', 'نشط')
    
    if not all([name, age, gender, phone, address]):
        flash('يرجى ملء جميع الحقول المطلوبة', 'error')
        return redirect(url_for('patient.add'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_date = date.today().isoformat()
    
    if patient_id:  # تحديث
        cursor.execute('''
            UPDATE patients 
            SET name = ?, age = ?, gender = ?, phone = ?, address = ?, 
                diagnosis = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (name, age, gender, phone, address, diagnosis, status, current_date, patient_id))
        
        flash('تم تحديث بيانات المريض بنجاح', 'success')
    else:  # إضافة جديدة
        # توليد رقم ملف جديد
        cursor.execute("SELECT COUNT(*) FROM patients WHERE strftime('%Y', created_at) = ?", 
                      (str(date.today().year),))
        year_count = cursor.fetchone()[0] + 1
        file_number = f"PT-{date.today().year}-{year_count:03d}"
        
        cursor.execute('''
            INSERT INTO patients (file_number, name, age, gender, phone, address, 
                                  diagnosis, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_number, name, age, gender, phone, address, diagnosis, status, current_date, current_date))
        
        flash('تم إضافة المريض بنجاح', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('patient.index'))

@patient_bp.route('/delete', methods=['POST'])
def delete():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لحذف المرضى', 'error')
        return redirect(url_for('patient.index'))
    
    patient_id = request.form.get('item_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
    
    flash('تم حذف المريض بنجاح', 'success')
    return redirect(url_for('patient.index'))

@patient_bp.route('/clear-temp', methods=['POST'])
def clear_temp():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لمسح البيانات المؤقتة', 'error')
        return redirect(url_for('patient.index'))
    
    flash('تم مسح البيانات المؤقتة بنجاح', 'success')
    return redirect(url_for('patient.index'))

@patient_bp.route('/api/search')
def search():
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
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        cursor.execute('''
            SELECT id, file_number, name, age, phone
            FROM patients 
            LIMIT 10
        ''')
    
    patients = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(patient) for patient in patients])