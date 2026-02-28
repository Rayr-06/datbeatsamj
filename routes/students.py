from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User

bp = Blueprint('students', __name__, url_prefix='/students')

@bp.route('/')
@login_required
def list_students():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    students = User.query.filter_by(role='student').all()
    return render_template('students/list.html', students=students)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        phone = request.form.get('phone', '')
        password = request.form.get('password', 'welcome123')
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
        else:
            hashed = generate_password_hash(password)
            student = User(email=email, name=name, phone=phone, password_hash=hashed, role='student')
            db.session.add(student)
            db.session.commit()
            flash(f'Student {name} added successfully. Initial password: {password}', 'success')
        return redirect(url_for('students.list_students'))
    return render_template('students/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    student = User.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.phone = request.form.get('phone', '')
        db.session.commit()
        flash('Student updated', 'success')
        return redirect(url_for('students.list_students'))
    return render_template('students/edit.html', student=student)

@bp.route('/delete/<int:id>')
@login_required
def delete_student(id):
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    student = User.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted', 'info')
    return redirect(url_for('students.list_students'))