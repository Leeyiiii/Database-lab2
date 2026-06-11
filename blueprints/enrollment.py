from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query

enrollment_bp = Blueprint('enrollment', __name__)


@enrollment_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    rows = query('''SELECT e.enrollment_id, e.student_id, s.name AS student_name,
                    e.course_id, c.course_name, e.semester
                    FROM Enrollment e
                    JOIN Student s ON e.student_id = s.student_id
                    JOIN Course c ON e.course_id = c.course_id
                    ORDER BY e.enrollment_id DESC''', fetchall=True)
    return render_template('enrollment_list.html', enrollments=rows)


@enrollment_bp.route('/create', methods=['POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    sid = request.form.get('student_id', '').strip()
    cid = request.form.get('course_id', '').strip()
    sem = request.form.get('semester', '').strip()
    try:
        query('INSERT INTO Enrollment (student_id, course_id, semester) VALUES (%s,%s,%s)',
              (sid, cid, sem))
        flash('选课记录添加成功')
    except Exception as e:
        flash(f'添加失败: {e}')
    return redirect(url_for('enrollment.list'))


@enrollment_bp.route('/delete/<int:eid>')
def delete(eid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        query('DELETE FROM Enrollment WHERE enrollment_id=%s', (eid,))
        flash('选课记录已删除')
    except Exception as e:
        flash(f'删除失败: {e}')
    return redirect(url_for('enrollment.list'))