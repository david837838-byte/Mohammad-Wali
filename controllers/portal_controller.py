from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.patient import Patient
from models.visit import Visit

portal_bp = Blueprint('portal', __name__, url_prefix='/portal')

@portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        file_number = request.form.get('file_number')
        patient = Patient.get_by_file_number(file_number)
        
        if patient:
            session['portal_patient_id'] = patient.id
            session['portal_patient_name'] = patient.name
            return redirect(url_for('portal.dashboard'))
        else:
            flash('رقم الملف غير صحيح', 'error')
            
    return render_template('portal/login.html')

@portal_bp.route('/dashboard')
def dashboard():
    if 'portal_patient_id' not in session:
        return redirect(url_for('portal.login'))
        
    patient = Patient.get_by_id(session['portal_patient_id'])
    
    # يمكن هنا جلب المواعيد والنتائج الخاصة بالمريض
    return render_template('portal/dashboard.html', patient=patient)

@portal_bp.route('/logout')
def logout():
    session.pop('portal_patient_id', None)
    session.pop('portal_patient_name', None)
    return redirect(url_for('portal.login'))
