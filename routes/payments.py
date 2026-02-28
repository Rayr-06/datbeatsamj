from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import Payment, User, Appointment
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/')
@login_required
def list_payments():
    if current_user.role == 'teacher':
        payments = Payment.query.order_by(Payment.date.desc()).all()
    else:
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.date.desc()).all()
    return render_template('payments/list.html', payments=payments)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    students = User.query.filter_by(role='student').all()
    appointments = Appointment.query.filter_by(status='completed').all()
    if request.method == 'POST':
        user_id = request.form['user_id']
        amount = float(request.form['amount'])
        method = request.form['method']
        appointment_id = request.form.get('appointment_id') or None
        notes = request.form.get('notes', '')
        payment = Payment(
            user_id=user_id,
            amount=amount,
            method=method,
            appointment_id=appointment_id,
            notes=notes
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded', 'success')
        return redirect(url_for('payments.list_payments'))
    return render_template('payments/add.html', students=students, appointments=appointments)

@bp.route('/student/<int:student_id>')
@login_required
def student_payments(student_id):
    if current_user.role != 'teacher' and current_user.id != student_id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    student = User.query.get_or_404(student_id)
    payments = Payment.query.filter_by(user_id=student_id).order_by(Payment.date.desc()).all()
    total = sum(p.amount for p in payments)
    return render_template('payments/student.html', student=student, payments=payments, total=total)