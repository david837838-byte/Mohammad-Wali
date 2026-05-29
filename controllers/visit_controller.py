from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_handler import get_db_connection
from datetime import datetime, date
import json

visit_bp = Blueprint('visit', __name__, url_prefix='/visits')

@visit_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.id, v.patient_id, v.date, v.time, v.purpose, 
               v.diagnosis, v.prescription, v.status, v.created_at,
               p.name as patient_name, p.file_number as patient_file_number,
               u.full_name as doctor_name
        FROM visits v
        LEFT JOIN patients p ON v.patient_id = p.id
        LEFT JOIN users u ON v.doctor_id = u.id
        ORDER BY v.date DESC, v.time DESC
    ''')
    visits = cursor.fetchall()
    
    conn.close()
    
    return render_template('visits.html', visits=visits)

@visit_bp.route('/api/today')
def today_visits():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    today = date.today().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.id, v.patient_id, v.date, v.time, v.purpose, 
               v.status, p.name as patient_name
        FROM visits v
        LEFT JOIN patients p ON v.patient_id = p.id
        WHERE v.date = ?
        ORDER BY v.time
    ''', (today,))
    
    visits = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(visit) for visit in visits])

@visit_bp.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO visits (patient_id, doctor_id, date, time, purpose, diagnosis, prescription, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['patient_id'],
                session.get('user_id'),
                request.form['date'],
                request.form['time'],
                request.form['purpose'],
                request.form.get('diagnosis', ''),
                request.form.get('prescription', ''),
                'مجدول',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            flash('تم إضافة الزيارة بنجاح', 'success')
            return redirect(url_for('visit.index'))
        except Exception as e:
            flash(f'خطأ: {str(e)}', 'error')
    
    # Get patients list
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM patients ORDER BY name')
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('visit_form.html', patients=patients, mode='add')

@visit_bp.route('/view/<int:id>')
def view(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.*, p.name as patient_name, u.full_name as doctor_name
        FROM visits v
        LEFT JOIN patients p ON v.patient_id = p.id
        LEFT JOIN users u ON v.doctor_id = u.id
        WHERE v.id = ?
    ''', (id,))
    
    visit = cursor.fetchone()
    conn.close()
    
    if not visit:
        flash('الزيارة غير موجودة', 'error')
        return redirect(url_for('visit.index'))
    
    return render_template('visit_detail.html', visit=visit)

@visit_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM visits WHERE id = ?', (id,))
    visit = cursor.fetchone()
    
    if not visit:
        flash('الزيارة غير موجودة', 'error')
        conn.close()
        return redirect(url_for('visit.index'))
    
    if request.method == 'POST':
        try:
            cursor.execute('''
                UPDATE visits 
                SET patient_id = ?, date = ?, time = ?, purpose = ?, diagnosis = ?, prescription = ?, status = ?
                WHERE id = ?
            ''', (
                request.form['patient_id'],
                request.form['date'],
                request.form['time'],
                request.form['purpose'],
                request.form.get('diagnosis', ''),
                request.form.get('prescription', ''),
                request.form.get('status', 'مجدول'),
                id
            ))
            
            conn.commit()
            conn.close()
            
            flash('تم تحديث الزيارة بنجاح', 'success')
            return redirect(url_for('visit.index'))
        except Exception as e:
            flash(f'خطأ: {str(e)}', 'error')
    
    # Get patients list
    cursor.execute('SELECT id, name FROM patients ORDER BY name')
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('visit_form.html', visit=visit, patients=patients, mode='edit')

@visit_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('غير مصرح بحذف الزيارات', 'error')
        return redirect(url_for('visit.index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM visits WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        flash('تم حذف الزيارة بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ: {str(e)}', 'error')
    
    return redirect(url_for('visit.index'))