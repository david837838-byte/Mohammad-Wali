from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.invoice import Invoice
from utils.helpers import has_permission

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.before_request
def check_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if not has_permission(['admin', 'doctor', 'nurse']):
        flash('ليس لديك صلاحية للوصول لقسم المالية', 'error')
        return redirect(url_for('dashboard.index'))

@billing_bp.route('/')
def index():
    invoices = Invoice.get_all()
    return render_template('billing/index.html', invoices=invoices)

@billing_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        total_amount = float(request.form.get('total_amount', 0.0))
        paid_amount = float(request.form.get('paid_amount', 0.0))
        status = request.form.get('status', 'غير مدفوع')
        
        invoice = Invoice(patient_id=patient_id, total_amount=total_amount, 
                          paid_amount=paid_amount, status=status)
        invoice.save()
        flash('تم إصدار الفاتورة بنجاح', 'success')
        return redirect(url_for('billing.index'))
    return render_template('billing/add.html')
