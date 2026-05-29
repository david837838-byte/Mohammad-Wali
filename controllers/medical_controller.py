from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_handler import get_db_connection
from datetime import datetime, date
import json

medical_bp = Blueprint('medical', __name__, url_prefix='/medical')

@medical_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT mr.id, mr.patient_id, mr.diagnosis, mr.treatment, 
               mr.notes, mr.date, mr.doctor_id, mr.created_at,
               p.name as patient_name, p.file_number as patient_file_number,
               u.full_name as doctor_name
        FROM medical_records mr
        LEFT JOIN patients p ON mr.patient_id = p.id
        LEFT JOIN users u ON mr.doctor_id = u.id
        ORDER BY mr.date DESC, mr.created_at DESC
    ''')
    medical_records = cursor.fetchall()
    
    conn.close()
    
    return render_template('medical_records.html', medical_records=medical_records)

@medical_bp.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin', 'doctor', 'nurse']:
        flash('ليس لديك صلاحية لإضافة سجلات طبية', 'error')
        return redirect(url_for('medical.index'))
    
    if request.method == 'POST':
        # معالجة الحفظ
        patient_id = request.form.get('patient_id')
        diagnosis = request.form.get('diagnosis', '')
        treatment = request.form.get('treatment', '')
        notes = request.form.get('notes', '')
        
        if not patient_id:
            flash('يرجى اختيار المريض', 'error')
            return redirect(url_for('medical.add'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        doctor_id = session.get('user_id')
        current_date = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO medical_records (patient_id, diagnosis, treatment, notes, 
                                         doctor_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, diagnosis, treatment, notes, doctor_id, current_date, current_date))
        
        conn.commit()
        conn.close()
        
        flash('تم إضافة السجل الطبي بنجاح', 'success')
        return redirect(url_for('medical.index'))
    
    # GET request - عرض النموذج
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_number, name FROM patients ORDER BY name')
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('medical_form.html', patients=patients, form_type='add')

@medical_bp.route('/save', methods=['POST'])
def save():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin', 'doctor', 'nurse']:
        flash('ليس لديك صلاحية لإدارة السجلات الطبية', 'error')
        return redirect(url_for('medical.index'))
    
    record_id = request.form.get('record_id')
    patient_id = request.form.get('patient_id')
    diagnosis = request.form.get('diagnosis', '')
    treatment = request.form.get('treatment', '')
    notes = request.form.get('notes', '')
    record_date = request.form.get('date', date.today().isoformat())
    
    if not patient_id:
        flash('يرجى اختيار المريض', 'error')
        return redirect(url_for('medical.add'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_date = datetime.now().isoformat()
        
        if record_id:  # تحديث
            cursor.execute('''
                UPDATE medical_records 
                SET patient_id = ?, diagnosis = ?, treatment = ?, notes = ?, 
                    date = ?, updated_at = ?
                WHERE id = ?
            ''', (patient_id, diagnosis, treatment, notes, record_date, current_date, record_id))
            
            flash('تم تحديث السجل الطبي بنجاح', 'success')
        else:  # إضافة جديدة
            doctor_id = session.get('user_id')
            
            cursor.execute('''
                INSERT INTO medical_records (patient_id, diagnosis, treatment, notes, 
                                             date, doctor_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, diagnosis, treatment, notes, record_date, doctor_id, current_date, current_date))
            
            flash('تم إضافة السجل الطبي بنجاح', 'success')
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('medical.index'))
    
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('medical.add'))

@medical_bp.route('/<int:id>/view')
def view(id):
    """عرض تفاصيل السجل الطبي"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mr.id, mr.patient_id, mr.diagnosis, mr.treatment, 
                   mr.notes, mr.date, mr.doctor_id, mr.created_at, mr.updated_at,
                   p.name as patient_name, p.file_number as patient_file_number,
                   p.age, p.gender,
                   u.full_name as doctor_name
            FROM medical_records mr
            LEFT JOIN patients p ON mr.patient_id = p.id
            LEFT JOIN users u ON mr.doctor_id = u.id
            WHERE mr.id = ?
        ''', (id,))
        
        medical = cursor.fetchone()
        conn.close()
        
        if not medical:
            flash('السجل الطبي غير موجود', 'error')
            return redirect(url_for('medical.index'))
        
        return render_template('medical_detail.html', medical=medical)
    
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('medical.index'))

@medical_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """تعديل السجل الطبي"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin', 'doctor']:
        flash('ليس لديك صلاحية لتعديل السجلات الطبية', 'error')
        return redirect(url_for('medical.index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # معالجة التحديث
            patient_id = request.form.get('patient_id')
            diagnosis = request.form.get('diagnosis', '')
            treatment = request.form.get('treatment', '')
            notes = request.form.get('notes', '')
            
            if not patient_id:
                flash('يرجى اختيار المريض', 'error')
                return redirect(url_for('medical.edit', id=id))
            
            current_date = datetime.now().isoformat()
            cursor.execute('''
                UPDATE medical_records 
                SET patient_id = ?, diagnosis = ?, treatment = ?, notes = ?, updated_at = ?
                WHERE id = ?
            ''', (patient_id, diagnosis, treatment, notes, current_date, id))
            
            conn.commit()
            conn.close()
            
            flash('تم تحديث السجل الطبي بنجاح', 'success')
            return redirect(url_for('medical.index'))
        
        # GET request - عرض النموذج
        cursor.execute('''
            SELECT * FROM medical_records WHERE id = ?
        ''', (id,))
        medical = cursor.fetchone()
        
        if not medical:
            flash('السجل الطبي غير موجود', 'error')
            conn.close()
            return redirect(url_for('medical.index'))
        
        cursor.execute('SELECT id, file_number, name FROM patients ORDER BY name')
        patients = cursor.fetchall()
        conn.close()
        
        return render_template('medical_form.html', medical=medical, patients=patients, form_type='edit')
    
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('medical.index'))

@medical_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """حذف السجل الطبي"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') not in ['admin']:
        flash('ليس لديك صلاحية لحذف السجلات الطبية', 'error')
        return redirect(url_for('medical.index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM medical_records WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        flash('تم حذف السجل الطبي بنجاح', 'success')
    
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('medical.index'))