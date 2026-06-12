from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query
from datetime import date

portal_bp = Blueprint('portal', __name__)


def student_required():
    """检查学生是否已登录，未登录则重定向到登录页"""
    if session.get('role') != 'student' or 'student_id' not in session:
        return redirect(url_for('auth.login'))
    return None


# ==================== 1. 个人仪表盘 ====================

@portal_bp.route('/dashboard')
def dashboard():
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']
    # 获取学生完整信息（含专业名称）
    student = query('''
        SELECT s.*, m.major_name
        FROM Student s
        LEFT JOIN Major m ON s.major_id = m.major_id
        WHERE s.student_id = %s
    ''', (sid,), fetchone=True)

    # 统计：选课数、奖惩数
    course_count = query(
        'SELECT COUNT(*) FROM Enrollment WHERE student_id=%s', (sid,), fetchone=True
    )[0]
    rp_count = query(
        'SELECT COUNT(*) FROM RewardPunish WHERE student_id=%s', (sid,), fetchone=True
    )[0]

    return render_template('student_dashboard.html',
                           student=student,
                           course_count=course_count,
                           rp_count=rp_count)


# ==================== 2. 课程浏览 + 自助选课/退课 ====================

@portal_bp.route('/courses')
def courses():
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']

    # 所有课程
    all_courses = query('SELECT * FROM Course ORDER BY semester, course_id', fetchall=True)

    # 已选课程ID集合
    enrolled = query(
        'SELECT course_id FROM Enrollment WHERE student_id=%s', (sid,), fetchall=True
    )
    enrolled_set = {row[0] for row in enrolled}

    return render_template('student_courses.html',
                           courses=all_courses,
                           enrolled_set=enrolled_set)


@portal_bp.route('/enroll/<course_id>')
def enroll(course_id):
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']

    # 获取课程信息（获取学期）
    course = query('SELECT semester FROM Course WHERE course_id=%s', (course_id,), fetchone=True)
    if not course:
        flash('课程不存在')
        return redirect(url_for('portal.courses'))

    try:
        query('INSERT INTO Enrollment (student_id, course_id, semester) VALUES (%s, %s, %s)',
              (sid, course_id, course[0]))
        flash(f'选课成功！课程编号：{course_id}')
    except Exception as e:
        flash(f'选课失败（可能已选过此课程）：{e}')

    return redirect(url_for('portal.courses'))


@portal_bp.route('/drop/<int:enrollment_id>')
def drop(enrollment_id):
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']
    # 确保退的是自己的课
    row = query(
        'SELECT course_id FROM Enrollment WHERE enrollment_id=%s AND student_id=%s',
        (enrollment_id, sid), fetchone=True
    )
    if not row:
        flash('选课记录不存在或无权操作')
        return redirect(url_for('portal.courses'))

    query('DELETE FROM Enrollment WHERE enrollment_id=%s', (enrollment_id,))
    flash(f'退课成功！课程编号：{row[0]}')
    return redirect(url_for('portal.courses'))


@portal_bp.route('/drop_by_course/<course_id>', methods=['POST'])
def drop_by_course(course_id):
    """根据课程编号退课（学生端AJAX调用）"""
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']
    row = query(
        'SELECT enrollment_id FROM Enrollment WHERE student_id=%s AND course_id=%s',
        (sid, course_id), fetchone=True
    )
    if not row:
        flash('选课记录不存在')
    else:
        query('DELETE FROM Enrollment WHERE enrollment_id=%s', (row[0],))
        flash(f'退课成功！课程编号：{course_id}')

    return redirect(url_for('portal.courses'))


# ==================== 3. 转专业申请 ====================

@portal_bp.route('/major_change', methods=['GET', 'POST'])
def major_change():
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']

    # 获取当前专业
    student = query('SELECT major_id FROM Student WHERE student_id=%s', (sid,), fetchone=True)
    current_major_id = student[0] if student else None

    if request.method == 'POST':
        new_major_id = request.form.get('new_major_id', '').strip()
        reason = request.form.get('reason', '').strip()

        if not new_major_id:
            flash('请选择目标专业')
            return redirect(url_for('portal.major_change'))
        if new_major_id == current_major_id:
            flash('目标专业与当前专业相同，无需转专业')
            return redirect(url_for('portal.major_change'))

        try:
            query('''
                INSERT INTO MajorChange (student_id, old_major_id, new_major_id, change_date, reason, status)
                VALUES (%s, %s, %s, %s, %s, '待审批')
            ''', (sid, current_major_id, new_major_id, date.today(), reason))
            flash('转专业申请已提交，等待管理员审批！')
        except Exception as e:
            flash(f'申请提交失败：{e}')

        return redirect(url_for('portal.major_change'))

    # GET：获取所有专业列表和历史申请
    all_majors = query('SELECT * FROM Major ORDER BY major_id', fetchall=True)
    history = query('''
        SELECT mc.*, m1.major_name AS old_name, m2.major_name AS new_name
        FROM MajorChange mc
        LEFT JOIN Major m1 ON mc.old_major_id = m1.major_id
        LEFT JOIN Major m2 ON mc.new_major_id = m2.major_id
        WHERE mc.student_id = %s
        ORDER BY mc.change_date DESC
    ''', (sid,), fetchall=True)

    return render_template('student_major_change.html',
                           all_majors=all_majors,
                           current_major_id=current_major_id,
                           history=history)


# ==================== 4. 成绩查询 ====================

@portal_bp.route('/scores')
def scores():
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']

    rows = query('''
        SELECT c.course_id, c.course_name, c.credits, e.semester,
               s.usual_score, s.final_score, s.total_score
        FROM Enrollment e
        JOIN Course c ON e.course_id = c.course_id
        LEFT JOIN Score s ON e.enrollment_id = s.enrollment_id
        WHERE e.student_id = %s
        ORDER BY e.semester, c.course_id
    ''', (sid,), fetchall=True)

    # 计算GPA
    total_points = 0.0
    total_credits = 0.0
    for r in rows:
        credit = float(r[2]) if r[2] else 0
        score = float(r[6]) if r[6] else 0
        if score >= 90:
            gp = 4.0
        elif score >= 85:
            gp = 3.7
        elif score >= 82:
            gp = 3.3
        elif score >= 78:
            gp = 3.0
        elif score >= 75:
            gp = 2.7
        elif score >= 72:
            gp = 2.3
        elif score >= 68:
            gp = 2.0
        elif score >= 64:
            gp = 1.5
        elif score >= 60:
            gp = 1.0
        else:
            gp = 0.0
        total_points += gp * credit
        total_credits += credit

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    return render_template('student_scores.html', scores=rows, gpa=gpa, total_credits=total_credits)


# ==================== 5. 奖惩记录 ====================

@portal_bp.route('/rewards')
def rewards():
    redirect_resp = student_required()
    if redirect_resp:
        return redirect_resp

    sid = session['student_id']
    rows = query('''
        SELECT record_id, type, name, description, date
        FROM RewardPunish
        WHERE student_id = %s
        ORDER BY date DESC
    ''', (sid,), fetchall=True)

    return render_template('student_rewards.html', rewards=rows)