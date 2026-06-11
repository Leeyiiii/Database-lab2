from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query
from config import UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, ALLOWED_DOC_EXTENSIONS
import os
from werkzeug.utils import secure_filename

rp_bp = Blueprint('reward_punish', __name__)

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@rp_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    search = request.args.get('search', '')
    rtype = request.args.get('type', '')
    where = 'WHERE 1=1'
    params = []
    if search:
        where += ' AND (rp.student_id LIKE %s OR st.name LIKE %s)'
        like = f'%{search}%'
        params.extend([like, like])
    if rtype:
        where += ' AND rp.type=%s'
        params.append(rtype)
    rows = query(f'''SELECT rp.record_id, rp.student_id, st.name AS student_name, rp.type,
                     rp.name, rp.description, rp.date, rp.evidence_path
                     FROM RewardPunish rp JOIN Student st ON rp.student_id = st.student_id
                     {where} ORDER BY rp.date DESC''', params, fetchall=True)
    return render_template('rp_list.html', records=rows, search=search, rtype=rtype)

@rp_bp.route('/create', methods=['GET', 'POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        sid = request.form.get('student_id', '')
        rtype = request.form.get('type', '')
        name = request.form.get('name', '')
        desc = request.form.get('description', '')
        date = request.form.get('date', '')
        paths = []
        for field in ['evidence_image', 'evidence_video', 'evidence_file']:
            if field in request.files:
                for file in request.files.getlist(field):
                    if file.filename:
                        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                        if 'image' in field:
                            allowed = ALLOWED_IMAGE_EXTENSIONS
                        elif 'video' in field:
                            allowed = ALLOWED_VIDEO_EXTENSIONS
                        else:
                            allowed = ALLOWED_DOC_EXTENSIONS
                        if ext in allowed:
                            fn = secure_filename(f'{sid}_{rtype}_{file.filename}')
                            file.save(os.path.join(UPLOAD_FOLDER, fn))
                            paths.append('uploads/' + fn)
        evidence = ','.join(paths) if paths else None
        query('''INSERT INTO RewardPunish (student_id, type, name, description, date, evidence_path)
                 VALUES (%s,%s,%s,%s,%s,%s)''', (sid, rtype, name, desc, date, evidence))
        flash('奖惩记录添加成功')
        return redirect(url_for('reward_punish.list'))
    students = query('SELECT student_id, name FROM Student WHERE is_deleted=0 ORDER BY student_id', fetchall=True)
    return render_template('rp_create.html', students=students)

@rp_bp.route('/edit/<int:rid>', methods=['GET', 'POST'])
def edit(rid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        sid = request.form.get('student_id', '')
        rtype = request.form.get('type', '')
        name = request.form.get('name', '')
        desc = request.form.get('description', '')
        date = request.form.get('date', '')
        paths_str = request.form.get('existing_paths', '')
        paths = [p for p in paths_str.split(',') if p] if paths_str else []
        for field in ['evidence_image', 'evidence_video', 'evidence_file']:
            if field in request.files:
                for file in request.files.getlist(field):
                    if file.filename:
                        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                        if 'image' in field:
                            allowed = ALLOWED_IMAGE_EXTENSIONS
                        elif 'video' in field:
                            allowed = ALLOWED_VIDEO_EXTENSIONS
                        else:
                            allowed = ALLOWED_DOC_EXTENSIONS
                        if ext in allowed:
                            fn = secure_filename(f'{sid}_{rtype}_{file.filename}')
                            file.save(os.path.join(UPLOAD_FOLDER, fn))
                            paths.append('uploads/' + fn)
        evidence = ','.join(paths) if paths else None
        query('''UPDATE RewardPunish SET student_id=%s, type=%s, name=%s, description=%s,
                 date=%s, evidence_path=%s WHERE record_id=%s''',
              (sid, rtype, name, desc, date, evidence, rid))
        flash('奖惩记录已更新')
        return redirect(url_for('reward_punish.list'))
    row = query('SELECT * FROM RewardPunish WHERE record_id=%s', (rid,), fetchone=True)
    students = query('SELECT student_id, name FROM Student WHERE is_deleted=0 ORDER BY student_id', fetchall=True)
    return render_template('rp_edit.html', r=row, students=students)

@rp_bp.route('/delete/<int:rid>')
def delete(rid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('DELETE FROM RewardPunish WHERE record_id=%s', (rid,))
    flash('奖惩记录已删除')
    return redirect(url_for('reward_punish.list'))