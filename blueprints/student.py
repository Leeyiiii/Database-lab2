from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query
from config import UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOC_EXTENSIONS
import os
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@student_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'student_id')
    order = request.args.get('order', 'asc')
    allowed_sorts = ['student_id', 'name', 'gender', 'enrollment_date']
    if sort not in allowed_sorts:
        sort = 'student_id'
    if order not in ['asc', 'desc']:
        order = 'asc'
    where = 'WHERE s.is_deleted = 0'
    params = []
    if search:
        where += ' AND (s.student_id LIKE %s OR s.name LIKE %s OR s.major_id LIKE %s)'
        like = f'%{search}%'
        params = [like, like, like]
    count_sql = f'SELECT COUNT(*) FROM Student s {where}'
    total = query(count_sql, params, fetchone=True)[0]
    total_pages = max(1, (total + per_page - 1) // per_page)
    sql = f'''SELECT s.student_id, s.name, s.gender, s.birth_date, s.phone, s.email,
               s.enrollment_date, m.major_name
        FROM Student s LEFT JOIN Major m ON s.major_id = m.major_id
        {where} ORDER BY s.{sort} {order} LIMIT {per_page} OFFSET {offset}'''
    rows = query(sql, params, fetchall=True)
    return render_template('student_list.html', students=rows, page=page,
                           total_pages=total_pages, search=search, sort=sort, order=order)

@student_bp.route('/view/<sid>')
def view(sid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    row = query('''SELECT s.*, m.major_name FROM Student s
                   LEFT JOIN Major m ON s.major_id = m.major_id
                   WHERE s.student_id=%s''', (sid,), fetchone=True)
    if not row:
        flash('学生不存在')
        return redirect(url_for('student.list'))
    return render_template('student_view.html', s=row)

@student_bp.route('/create', methods=['GET', 'POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        sid = request.form.get('student_id', '')
        name = request.form.get('name', '')
        gender = request.form.get('gender', '')
        birth = request.form.get('birth_date', '') or None
        id_card = request.form.get('id_card', '') or None
        native = request.form.get('native_place', '') or None
        ethnicity = request.form.get('ethnicity', '') or None
        political = request.form.get('political_status', '') or None
        phone = request.form.get('phone', '') or None
        email = request.form.get('email', '') or None
        address = request.form.get('home_address', '') or None
        enrollment = request.form.get('enrollment_date', '') or None
        major_id = request.form.get('major_id', '') or None
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                fn = secure_filename(sid + '_photo_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                photo_path = 'uploads/' + fn
        resume_path = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
                fn = secure_filename(sid + '_resume_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                resume_path = 'uploads/' + fn
        try:
            query('''INSERT INTO Student (student_id,name,gender,birth_date,id_card,native_place,
                     ethnicity,political_status,phone,email,home_address,photo_path,resume_path,
                     enrollment_date,major_id)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                  (sid, name, gender, birth, id_card, native, ethnicity, political, phone, email,
                   address, photo_path, resume_path, enrollment, major_id))
            flash('学生信息录入成功')
        except Exception as e:
            flash(f'录入失败: {e}')
        return redirect(url_for('student.list'))
    majors = query('SELECT major_id, major_name FROM Major ORDER BY major_id', fetchall=True)
    return render_template('student_create.html', majors=majors)

@student_bp.route('/edit/<sid>', methods=['GET', 'POST'])
def edit(sid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('name', '')
        gender = request.form.get('gender', '')
        birth = request.form.get('birth_date', '') or None
        id_card = request.form.get('id_card', '') or None
        native = request.form.get('native_place', '') or None
        ethnicity = request.form.get('ethnicity', '') or None
        political = request.form.get('political_status', '') or None
        phone = request.form.get('phone', '') or None
        email = request.form.get('email', '') or None
        address = request.form.get('home_address', '') or None
        enrollment = request.form.get('enrollment_date', '') or None
        major_id = request.form.get('major_id', '') or None
        old = query('SELECT photo_path, resume_path FROM Student WHERE student_id=%s', (sid,), fetchone=True)
        photo_path = old[0] if old else None
        resume_path = old[1] if old else None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                fn = secure_filename(sid + '_photo_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                photo_path = 'uploads/' + fn
        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
                fn = secure_filename(sid + '_resume_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                resume_path = 'uploads/' + fn
        query('''UPDATE Student SET name=%s,gender=%s,birth_date=%s,id_card=%s,native_place=%s,
                 ethnicity=%s,political_status=%s,phone=%s,email=%s,home_address=%s,
                 photo_path=%s,resume_path=%s,enrollment_date=%s,major_id=%s WHERE student_id=%s''',
              (name, gender, birth, id_card, native, ethnicity, political, phone, email,
               address, photo_path, resume_path, enrollment, major_id, sid))
        flash('学生信息修改成功')
        return redirect(url_for('student.list'))
    row = query('SELECT * FROM Student WHERE student_id=%s', (sid,), fetchone=True)
    majors = query('SELECT major_id, major_name FROM Major ORDER BY major_id', fetchall=True)
    return render_template('student_edit.html', s=row, majors=majors)

@student_bp.route('/delete/<sid>')
def delete(sid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('UPDATE Student SET is_deleted=1 WHERE student_id=%s', (sid,))
    flash('学生已归档（软删除）')
    return redirect(url_for('student.list'))