from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db_handler import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # البحث عن المستخدم
        cursor.execute('''
            SELECT id, full_name, username, password, role, status 
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # في هذا المثال، نقارن كلمات المرور مباشرة (بدون تشفير)
            # في تطبيق حقيقي، استخدم check_password_hash
            if user['password'] == password:
                if user['status'] != 'نشط':
                    flash('حسابك غير نشط، يرجى التواصل مع المدير', 'error')
                    return render_template('login.html')
                
                # حفظ بيانات الجلسة
                session['user_id'] = user['id']
                session['user_name'] = user['username']
                session['user_full_name'] = user['full_name']
                session['user_role'] = user['role']
                session.permanent = True
                
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('كلمة المرور غير صحيحة', 'error')
        else:
            # بيانات اختبار افتراضية
            if username == 'admin' and password == 'admin123':
                session['user_id'] = 1
                session['user_name'] = 'admin'
                session['user_full_name'] = 'مدير النظام'
                session['user_role'] = role
                session.permanent = True
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard.index'))
            elif username == 'doctor1' and password == 'doctor123':
                session['user_id'] = 2
                session['user_name'] = 'doctor1'
                session['user_full_name'] = 'د. محمد أحمد'
                session['user_role'] = 'doctor'
                session.permanent = True
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard.index'))
            elif username == 'nurse1' and password == 'nurse123':
                session['user_id'] = 3
                session['user_name'] = 'nurse1'
                session['user_full_name'] = 'ممرضة سارة'
                session['user_role'] = 'nurse'
                session.permanent = True
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard.index'))
            elif username == 'viewer' and password == 'view123':
                session['user_id'] = 4
                session['user_name'] = 'viewer'
                session['user_full_name'] = 'مشاهد النظام'
                session['user_role'] = 'view'
                session.permanent = True
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth.login'))