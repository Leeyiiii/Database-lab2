from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query
from config import UPLOAD_FOLDER, ALLOWED_DOC_EXTENSIONS
import os
from werkzeug.utils import secure_filename

course_bp = Blueprint('course', __name__)


def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


@course_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'course_id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    allowed_sorts = ['course_id', 'course_name', 'credits', 'hours', 'course_type', 'semester', 'teacher']
    if sort not in allowed_sorts:
        sort = 'course_id'
    if order not in ('asc', 'desc'):
        order = 'asc'

    where = 'WHERE 1=1'
    params = []
    if search:
        where += ' AND (course_id LIKE %s OR course_name LIKE %s OR teacher LIKE %s)'
        like = f'%{search}%'
        params = [like, like, like]

    count_row = query(f'SELECT COUNT(*) FROM Course {where}', params, fetchone=True)
    total = count_row[0] if count_row else 0
    total_pages = max(1, (total + per_page - 1) // per_page)
    offset = (page - 1) * per_page

    rows = query(f'SELECT * FROM Course {where} ORDER BY {sort} {order} LIMIT %s OFFSET %s',
                 params + [per_page, offset], fetchall=True)
    return render_template('course_list.html', courses=rows, search=search,
                           sort=sort, order=order, page=page, total_pages=total_pages)


@course_bp.route('/create', methods=['POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    cid = request.form.get('course_id', '')
    name = request.form.get('course_name', '')
    credits = request.form.get('credits', 0)
    hours = request.form.get('hours', 0)
    course_type = request.form.get('course_type', '必修')
    teacher = request.form.get('teacher', '')
    semester = request.form.get('semester', '')
    desc = request.form.get('description', '')
    syllabus_path = None
    if 'syllabus' in request.files:
        file = request.files['syllabus']
        if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
            fn = secure_filename(cid + '_syllabus_' + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, fn))
            syllabus_path = 'uploads/' + fn
    material_paths = []
    if 'material' in request.files:
        for file in request.files.getlist('material'):
            if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
                fn = secure_filename(cid + '_material_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                material_paths.append('uploads/' + fn)
    material_path = ','.join(material_paths) if material_paths else None
    try:
        query('''INSERT INTO Course (course_id, course_name, credits, hours, course_type,
                 semester, teacher, syllabus_path, material_path, description)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
              (cid, name, credits, hours, course_type, semester, teacher, syllabus_path, material_path, desc))
        flash('课程添加成功')
    except Exception as e:
        flash(f'添加失败: {e}')
    return redirect(url_for('course.list'))


@course_bp.route('/edit/<cid>', methods=['POST'])
def edit(cid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('course_name', '')
    credits = request.form.get('credits', 0)
    hours = request.form.get('hours', 0)
    course_type = request.form.get('course_type', '必修')
    teacher = request.form.get('teacher', '')
    semester = request.form.get('semester', '')
    desc = request.form.get('description', '')
    old = query('SELECT syllabus_path, material_path FROM Course WHERE course_id=%s', (cid,), fetchone=True)
    syllabus_path = old[0] if old else None
    material_path = old[1] if old else None
    if 'syllabus' in request.files:
        file = request.files['syllabus']
        if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
            fn = secure_filename(cid + '_syllabus_' + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, fn))
            syllabus_path = 'uploads/' + fn
    if 'material' in request.files:
        paths = [p for p in (material_path or '').split(',') if p]
        for file in request.files.getlist('material'):
            if file.filename and allowed_file(file.filename, ALLOWED_DOC_EXTENSIONS):
                fn = secure_filename(cid + '_material_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fn))
                paths.append('uploads/' + fn)
        material_path = ','.join(paths) if paths else None
    query('''UPDATE Course SET course_name=%s, credits=%s, hours=%s, course_type=%s,
             semester=%s, teacher=%s, syllabus_path=%s, material_path=%s, description=%s
             WHERE course_id=%s''',
          (name, credits, hours, course_type, semester, teacher, syllabus_path, material_path, desc, cid))
    flash('课程信息已更新')
    return redirect(url_for('course.list'))


@course_bp.route('/delete/<cid>')
def delete(cid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('DELETE FROM Course WHERE course_id=%s', (cid,))
    flash('课程已删除')
    return redirect(url_for('course.list'))