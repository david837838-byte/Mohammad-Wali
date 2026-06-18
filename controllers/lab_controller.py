from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.lab import LabTest, LabRequest
from utils.helpers import has_permission

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

@lab_bp.before_request
def check_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if not has_permission(['admin', 'doctor', 'nurse']):
        flash('ليس لديك صلاحية للوصول للمختبر', 'error')
        return redirect(url_for('dashboard.index'))

@lab_bp.route('/')
def index():
    requests = LabRequest.get_all()
    return render_template('lab/index.html', requests=requests)

@lab_bp.route('/tests')
def tests():
    tests_list = LabTest.get_all()
    return render_template('lab/tests.html', tests=tests_list)
