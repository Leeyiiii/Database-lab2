from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query, callproc, insert_return_id

score_bp = Blueprint('score', __name__)


@score_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    search = request.args.get('search', '')
    where = 'WHERE 1=1'
    params = []
    if search:
        where += ' AND (e.student_id LIKE %s OR st.name LIKE %s OR e.course_id LIKE %s OR c.course_name LIKE %s)'
        like = f'%{search}%'
        params = [like, like, like, like]
    sql = f'''SELECT sc.score_id, e.student_id, st.name AS student_name, e.course_id,
                     c.course_name, sc.usual_score, sc.final_score, sc.total_score,
                     e.semester
              FROM Score sc
              JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
              JOIN Student st ON e.student_id = st.student_id
              JOIN Course c ON e.course_id = c.course_id
              {where} ORDER BY e.semester DESC, e.student_id, e.course_id'''
    rows = query(sql, params, fetchall=True)
    students = query('SELECT student_id, name FROM Student ORDER BY student_id', fetchall=True) or []
    courses = query('SELECT course_id, course_name, semester FROM Course ORDER BY course_id', fetchall=True) or []
    return render_template('score_list.html', scores=rows, search=search, students=students, courses=courses)


@score_bp.route('/create', methods=['POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    sid = request.form.get('student_id', '')
    cid = request.form.get('course_id', '')
    usual = request.form.get('usual_score', 0)
    final = request.form.get('final_score', 0)
    sem = request.form.get('semester', '')
    # 输入验证
    if not sid or not cid or not sem:
        flash('学号、课程编号和学期不能为空')
        return redirect(url_for('score.list'))
    # 验证学生是否存在
    student = query('SELECT student_id FROM Student WHERE student_id=%s AND is_deleted=0', (sid,), fetchone=True)
    if not student:
        flash(f'学号 {sid} 不存在或已被删除')
        return redirect(url_for('score.list'))
    # 验证课程是否存在
    course = query('SELECT course_id FROM Course WHERE course_id=%s', (cid,), fetchone=True)
    if not course:
        flash(f'课程编号 {cid} 不存在')
        return redirect(url_for('score.list'))
    try:
        # 先检查选课记录是否存在
        enroll = query(
            'SELECT enrollment_id FROM Enrollment WHERE student_id=%s AND course_id=%s AND semester=%s',
            (sid, cid, sem), fetchone=True)
        if not enroll:
            eid = insert_return_id(
                'INSERT INTO Enrollment (student_id, course_id, semester) VALUES (%s,%s,%s)',
                (sid, cid, sem))
        else:
            eid = enroll[0]
        # 检查是否已有成绩
        existing = query('SELECT score_id FROM Score WHERE enrollment_id=%s', (eid,), fetchone=True)
        if existing:
            flash('该学生此课程已有成绩，请使用编辑功能')
        else:
            query('INSERT INTO Score (enrollment_id, usual_score, final_score) VALUES (%s,%s,%s)',
                  (eid, usual, final))
            flash('成绩录入成功（总评已自动计算）')
    except Exception as e:
        flash(f'录入失败: {e}')
    return redirect(url_for('score.list'))


@score_bp.route('/edit/<int:sid>', methods=['POST'])
def edit(sid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    usual = request.form.get('usual_score', 0)
    final = request.form.get('final_score', 0)
    try:
        query('UPDATE Score SET usual_score=%s, final_score=%s WHERE score_id=%s',
              (usual, final, sid))
        flash('成绩更新成功（总评已自动重新计算）')
    except Exception as e:
        flash(f'更新失败: {e}')
    return redirect(url_for('score.list'))


@score_bp.route('/delete/<int:sid>')
def delete(sid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('DELETE FROM Score WHERE score_id=%s', (sid,))
    flash('成绩已删除')
    return redirect(url_for('score.list'))


@score_bp.route('/gpa')
def gpa():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    sid_filter = request.args.get('student_id', '')
    
    rows = query('''SELECT s.student_id, s.name,
                     fn_avg_score(s.student_id) AS avg_score,
                     fn_course_count(s.student_id) AS course_count
              FROM Student s WHERE s.is_deleted = 0 ORDER BY s.student_id''', fetchall=True)
    
    gpas = []
    semesters_data = {}  # {student_id: [(semester, semester_gpa, credits, count), ...]}
    
    for r in rows:
        sid_val = r[0]
        gpa_result = callproc('sp_calc_gpa', (sid_val, 0.0))
        gpa_val = gpa_result[0] if gpa_result else 0
        gpas.append((r[0], r[1], r[2], gpa_val, r[3]))
        
        # 查询学期GPA
        sem_rows = callproc('sp_calc_semester_gpa', (sid_val,), fetch_result=True)
        if sem_rows:
            semesters_data[sid_val] = sem_rows
    
    # 过滤选中学生的详细数据
    detailed_semesters = []
    if sid_filter:
        detailed_semesters = semesters_data.get(sid_filter, [])
    
    students = query('SELECT student_id, name FROM Student WHERE is_deleted=0 ORDER BY student_id', fetchall=True) or []
    return render_template('score_gpa.html', gpas=gpas, semesters_data=semesters_data, 
                         detailed_semesters=detailed_semesters, sid_filter=sid_filter, students=students)


@score_bp.route('/rank')
def rank():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    cid = request.args.get('course_id', '')
    courses = query('SELECT course_id, course_name FROM Course ORDER BY course_id', fetchall=True)
    ranks = []
    if cid:
        ranks = callproc('sp_rank_by_course', (cid,), fetch_result=True)
    return render_template('score_rank.html', courses=courses, cid=cid, ranks=ranks)


@score_bp.route('/stats')
def stats():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    avg_rows = query('''SELECT c.course_id, c.course_name,
                         COUNT(sc.score_id) AS cnt,
                         ROUND(AVG(sc.total_score), 2) AS avg,
                         MAX(sc.total_score) AS max_s, MIN(sc.total_score) AS min_s
                  FROM Course c LEFT JOIN Enrollment e ON c.course_id = e.course_id
                  LEFT JOIN Score sc ON e.enrollment_id = sc.enrollment_id
                  GROUP BY c.course_id, c.course_name ORDER BY c.course_id''', fetchall=True)
    dist_rows = query('''SELECT
                          SUM(CASE WHEN sc.total_score >= 90 THEN 1 ELSE 0 END) AS A,
                          SUM(CASE WHEN sc.total_score >= 80 AND sc.total_score < 90 THEN 1 ELSE 0 END) AS B,
                          SUM(CASE WHEN sc.total_score >= 70 AND sc.total_score < 80 THEN 1 ELSE 0 END) AS C,
                          SUM(CASE WHEN sc.total_score >= 60 AND sc.total_score < 70 THEN 1 ELSE 0 END) AS D,
                          SUM(CASE WHEN sc.total_score < 60 THEN 1 ELSE 0 END) AS F,
                          COUNT(*) AS total
                       FROM Score sc''', fetchone=True)
    return render_template('score_stats.html', avg_rows=avg_rows, dist_rows=dist_rows)