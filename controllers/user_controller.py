from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_handler import get_db_connection
from models.permissions import UserPermissions
from datetime import datetime, date
import json

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية للوصول إلى إدارة المستخدمين', 'error')
        return redirect(url_for('dashboard.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, full_name, username, email, phone, role, status, created_at
        FROM users 
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('users.html', users=users)

@user_bp.route('/add')
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لإضافة مستخدمين', 'error')
        return redirect(url_for('user.index'))
    
    return render_template('user_form.html')

@user_bp.route('/edit/<int:id>')
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لتعديل بيانات المستخدمين', 'error')
        return redirect(url_for('user.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, full_name, username, email, phone, role, status, created_at
        FROM users 
        WHERE id = ?
    ''', (id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('user.index'))
    
    return render_template('user_form.html', user=user)

@user_bp.route('/save', methods=['POST'])
def save():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لإدارة المستخدمين', 'error')
        return redirect(url_for('user.index'))
    
    user_id = request.form.get('user_id')
    full_name = request.form.get('full_name')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    role = request.form.get('role')
    status = request.form.get('status', 'نشط')
    
    if not all([full_name, username, role]):
        flash('يرجى ملء جميع الحقول المطلوبة', 'error')
        return redirect(url_for('user.add'))
    
    if not user_id and not password:
        flash('يرجى إدخال كلمة المرور', 'error')
        return redirect(url_for('user.add'))
    
    if password and password != confirm_password:
        flash('كلمة المرور غير متطابقة', 'error')
        return redirect(url_for('user.add'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من عدم وجود اسم مستخدم مكرر
    if user_id:
        cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, user_id))
    else:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    
    if cursor.fetchone():
        flash('اسم المستخدم موجود مسبقاً، يرجى اختيار اسم آخر', 'error')
        conn.close()
        return redirect(url_for('user.add'))
    
    current_date = date.today().isoformat()
    
    if user_id:  # تحديث
        if password:
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, username = ?, password = ?, email = ?, 
                    phone = ?, role = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (full_name, username, password, email, phone, role, status, current_date, user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, username = ?, email = ?, phone = ?, 
                    role = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (full_name, username, email, phone, role, status, current_date, user_id))
        
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
    else:  # إضافة جديدة
        cursor.execute('''
            INSERT INTO users (full_name, username, password, email, phone, 
                              role, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, username, password, email, phone, role, status, current_date, current_date))
        
        flash('تم إضافة المستخدم بنجاح', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('user.index'))

@user_bp.route('/delete', methods=['POST'])
def delete():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لحذف المستخدمين', 'error')
        return redirect(url_for('user.index'))
    
    user_id = request.form.get('item_id')
    
    # منع حذف المستخدم الحالي
    if int(user_id) == session.get('user_id'):
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('user.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/permissions/<int:id>')
def manage_permissions(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية لإدارة الصلاحيات', 'error')
        return redirect(url_for('user.index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    
    if not user:
        flash('المستخدم غير موجود', 'error')
        conn.close()
        return redirect(url_for('user.index'))
    
    permissions = UserPermissions.get_by_user_id(id)
    conn.close()
    
    return render_template('user_permissions.html', user=dict(user), permissions=permissions)

@user_bp.route('/permissions/<int:id>/update', methods=['POST'])
def update_permissions(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    permissions_dict = {
        'can_view_patients': request.form.get('can_view_patients') == 'on',
        'can_add_patients': request.form.get('can_add_patients') == 'on',
        'can_edit_patients': request.form.get('can_edit_patients') == 'on',
        'can_delete_patients': request.form.get('can_delete_patients') == 'on',
        'can_view_medical': request.form.get('can_view_medical') == 'on',
        'can_add_medical': request.form.get('can_add_medical') == 'on',
        'can_edit_medical': request.form.get('can_edit_medical') == 'on',
        'can_delete_medical': request.form.get('can_delete_medical') == 'on',
        'can_view_visits': request.form.get('can_view_visits') == 'on',
        'can_add_visits': request.form.get('can_add_visits') == 'on',
        'can_edit_visits': request.form.get('can_edit_visits') == 'on',
        'can_delete_visits': request.form.get('can_delete_visits') == 'on',
        'can_view_reports': request.form.get('can_view_reports') == 'on',
        'can_manage_users': request.form.get('can_manage_users') == 'on',
        'can_manage_settings': request.form.get('can_manage_settings') == 'on',
    }
    
    UserPermissions.update_permissions(id, permissions_dict)
    flash('تم تحديث الصلاحيات بنجاح', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/api/current-user')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مصرح'}), 401
    
    return jsonify({
        'id': session.get('user_id'),
        'username': session.get('user_name'),
        'full_name': session.get('user_full_name'),
        'role': session.get('user_role')
    })