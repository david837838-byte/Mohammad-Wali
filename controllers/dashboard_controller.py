from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from database.db_handler import get_db_connection
from datetime import datetime, date
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب الإحصائيات
    cursor.execute('SELECT COUNT(*) FROM patients')
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor' AND status = 'نشط'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    today = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) FROM visits WHERE date = ?', (today,))
    today_visits = cursor.fetchone()[0]
    
    # جلب آخر المرضى المسجلين
    cursor.execute('''
        SELECT id, file_number, name, age, diagnosis, status, created_at
        FROM patients 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    recent_patients = cursor.fetchall()
    
    conn.close()
    
    # تحضير التاريخ الحالي بالعربية
    days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
    months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
              'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    
    now = datetime.now()
    current_date = f"{days[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
    
    return render_template('dashboard.html', 
                         stats={
                             'total_patients': total_patients,
                             'total_doctors': total_doctors,
                             'total_users': total_users,
                             'today_visits': today_visits
                         },
                         recent_patients=recent_patients,
                         current_date=current_date)

@dashboard_bp.route('/api/refresh-stats')
def refresh_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM patients')
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor' AND status = 'نشط'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
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