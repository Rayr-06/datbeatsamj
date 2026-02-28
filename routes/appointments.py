from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import Appointment, User
from datetime import datetime
from werkzeug.security import generate_password_hash

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/')
@login_required
def list_appointments():
    if current_user.role == 'teacher':
        appointments = Appointment.query.order_by(Appointment.start_time).all()
    else:
        appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.start_time).all()
    return render_template('appointments/list.html', appointments=appointments)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    students = User.query.filter_by(role='student').all() if current_user.role == 'teacher' else []
    if request.method == 'POST':
        user_id = request.form.get('user_id', current_user.id)
        title = request.form['title']
        description = request.form.get('description', '')
        app_type = request.form['appointment_type']
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time']) if request.form.get('end_time') else None
        status = request.form.get('status', 'pending')
        appointment = Appointment(
            user_id=user_id,
            title=title,
            description=description,
            appointment_type=app_type,
            start_time=start_time,
            end_time=end_time,
            status=status
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment created', 'success')
        return redirect(url_for('appointments.list_appointments'))
    return render_template('appointments/add.html', students=students)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if current_user.role != 'teacher' and appointment.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    students = User.query.filter_by(role='student').all() if current_user.role == 'teacher' else []
    if request.method == 'POST':
        appointment.title = request.form['title']
        appointment.description = request.form.get('description', '')
        appointment.appointment_type = request.form['appointment_type']
        appointment.start_time = datetime.fromisoformat(request.form['start_time'])
        appointment.end_time = datetime.fromisoformat(request.form['end_time']) if request.form.get('end_time') else None
        appointment.status = request.form.get('status', appointment.status)
        if current_user.role == 'teacher' and request.form.get('user_id'):
            appointment.user_id = request.form['user_id']
        db.session.commit()
        flash('Appointment updated', 'success')
        return redirect(url_for('appointments.list_appointments'))
    return render_template('appointments/edit.html', appointment=appointment, students=students)

@bp.route('/delete/<int:id>')
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if current_user.role != 'teacher' and appointment.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted', 'info')
    return redirect(url_for('appointments.list_appointments'))

@bp.route('/book-public', methods=['GET', 'POST'])
def book_public():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        app_type = request.form['appointment_type']
        start_time = datetime.fromisoformat(request.form['start_time'])
        # Create a temporary user or link to existing
        user = User.query.filter_by(email=email).first()
        if not user:
            # create a user with a random password; they can reset later
            import secrets
            temp_password = secrets.token_urlsafe(8)
            hashed = generate_password_hash(temp_password)
            user = User(email=email, name=name, phone=phone, password_hash=hashed, role='student')
            db.session.add(user)
            db.session.commit()
            # In real app, send email with temporary password
        appointment = Appointment(
            user_id=user.id,
            title=f"Public booking: {app_type}",
            description=request.form.get('description', ''),
            appointment_type=app_type,
            start_time=start_time,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Booking request sent! The teacher will confirm shortly.', 'success')
        return redirect(url_for('main.index'))
    return render_template('appointments/book_public.html')