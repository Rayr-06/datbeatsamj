from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Appointment, Payment
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        # Teacher dashboard
        students_count = User.query.filter_by(role='student').count()
        pending_appointments = Appointment.query.filter_by(status='pending').count()
        recent_payments = Payment.query.order_by(Payment.date.desc()).limit(5).all()
        upcoming_appointments = Appointment.query.filter(Appointment.start_time > datetime.utcnow()).order_by(Appointment.start_time).limit(10).all()
        return render_template('dashboard_teacher.html',
                               students_count=students_count,
                               pending_appointments=pending_appointments,
                               recent_payments=recent_payments,
                               upcoming_appointments=upcoming_appointments)
    else:
        # Student dashboard
        appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.start_time).all()
        return render_template('dashboard_student.html', appointments=appointments)