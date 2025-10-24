from flask import Blueprint, render_template, request, redirect, url_for, session
from . import db
from .models import Student, Attendance
from datetime import date
import os
from twilio.rest import Client
import threading
bp = Blueprint('main', __name__)
def send_absent_sms(phone, student_name, attendance_date):
    sid = os.getenv('TWILIO_ACCOUNT_SID')
    token = os.getenv('TWILIO_AUTH_TOKEN')
    from_num = os.getenv('TWILIO_FROM_NUMBER')
    if not sid or not token or not from_num:
        return
    client = Client(sid, token)
    body = f'Attendance alert: {student_name} was absent on {attendance_date}.'
    try:
        client.messages.create(body=body, from_=from_num, to=phone)
    except Exception:
        pass
@bp.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))
@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if u == os.getenv('TEACHER_USER','teacher') and p == os.getenv('TEACHER_PASS','password'):
            session['logged_in'] = True
            return redirect(url_for('main.dashboard'))
    return render_template('login.html')
@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.login'))
@bp.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        present_ids = request.form.getlist('present')
        today = date.today()
        students = Student.query.filter_by(class_name=class_name).with_entities(Student.id, Student.name, Student.phone).all()
        student_map = {str(s.id): (s.name, s.phone) for s in students}
        existing = Attendance.query.filter_by(date=today).join(Student).filter(Student.class_name==class_name).with_entities(Attendance.student_id).all()
        existing_set = {e.student_id for e in existing}
        records = []
        sms_tasks = []
        for sid_str, (name, phone) in student_map.items():
            sid = int(sid_str)
            if sid in existing_set:
                continue
            present = sid_str in present_ids
            records.append(Attendance(student_id=sid, date=today, present=present))
            if not present:
                sms_tasks.append((phone, name, today.isoformat()))
        if records:
            db.session.bulk_save_objects(records)
            db.session.commit()
        for phone, name, d in sms_tasks:
            threading.Thread(target=send_absent_sms, args=(phone,name,d), daemon=True).start()
        return redirect(url_for('main.dashboard'))
    classes = db.session.query(Student.class_name).distinct().all()
    classes = [c[0] for c in classes]
    selected = request.args.get('class', classes[0] if classes else None)
    students = []
    if selected:
        students = Student.query.filter_by(class_name=selected).order_by(Student.roll).all()
        today = date.today()
        present_ids = {a.student_id for a in Attendance.query.filter_by(date=today).join(Student).filter(Student.class_name==selected).with_entities(Attendance.student_id).all()}
    else:
        present_ids = set()
    return render_template('dashboard.html', classes=classes, students=students, selected=selected, present_ids=present_ids)
