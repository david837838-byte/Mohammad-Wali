from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.medicine import Medicine, Prescription
from utils.helpers import has_permission

pharmacy_bp = Blueprint('pharmacy', __name__, url_prefix='/pharmacy')

@pharmacy_bp.before_request
def check_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if not has_permission(['admin', 'doctor', 'nurse']):
        flash('ليس لديك صلاحية للوصول للصيدلية', 'error')
        return redirect(url_for('dashboard.index'))

@pharmacy_bp.route('/')
def index():
    medicines = Medicine.get_all()
    return render_template('pharmacy/index.html', medicines=medicines)

@pharmacy_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category', '')
        stock = int(request.form.get('stock', 0))
        expiry_date = request.form.get('expiry_date', '')
        price = float(request.form.get('price', 0.0))
        
        medicine = Medicine(name=name, category=category, stock=stock, 
                            expiry_date=expiry_date, price=price)
        medicine.save()
        flash('تم إضافة الدواء بنجاح', 'success')
        return redirect(url_for('pharmacy.index'))
    return render_template('pharmacy/add.html')

@pharmacy_bp.route('/prescriptions')
def prescriptions():
    prescriptions_list = Prescription.get_all()
    return render_template('pharmacy/prescriptions.html', prescriptions=prescriptions_list)
