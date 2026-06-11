from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query, transaction

major_bp = Blueprint('major', __name__)

@major_bp.route('/list')
def list():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    rows = query('SELECT * FROM Major ORDER BY major_id', fetchall=True)
    return render_template('major_list.html', majors=rows)

@major_bp.route('/create', methods=['POST'])
def create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    mid = request.form.get('major_id', '')
    name = request.form.get('major_name', '')
    dept = request.form.get('department', '')
    dur = request.form.get('duration', 4)
    try:
        query('INSERT INTO Major VALUES (%s,%s,%s,%s)', (mid, name, dept, dur))
        flash('专业添加成功')
    except Exception as e:
        flash(f'添加失败: {e}')
    return redirect(url_for('major.list'))

@major_bp.route('/edit/<mid>', methods=['POST'])
def edit(mid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('major_name', '')
    dept = request.form.get('department', '')
    dur = request.form.get('duration', 4)
    query('UPDATE Major SET major_name=%s, department=%s, duration=%s WHERE major_id=%s',
          (name, dept, dur, mid))
    flash('专业信息已更新')
    return redirect(url_for('major.list'))

@major_bp.route('/delete/<mid>')
def delete(mid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('DELETE FROM Major WHERE major_id=%s', (mid,))
    flash('专业已删除')
    return redirect(url_for('major.list'))

@major_bp.route('/changes')
def changes():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    search = request.args.get('search', '')
    where = 'WHERE 1=1'
    params = []
    if search:
        where += ' AND (mc.student_id LIKE %s OR st.name LIKE %s)'
        like = f'%{search}%'
        params = [like, like]
    rows = query(f'''SELECT mc.change_id, mc.student_id, st.name AS student_name,
                    mc.old_major_id, m1.major_name AS old_name,
                    mc.new_major_id, m2.major_name AS new_name,
                    mc.change_date, mc.reason, mc.status
                    FROM MajorChange mc
                    JOIN Student st ON mc.student_id = st.student_id
                    LEFT JOIN Major m1 ON mc.old_major_id = m1.major_id
                    LEFT JOIN Major m2 ON mc.new_major_id = m2.major_id
                    {where}
                    ORDER BY mc.change_date DESC''', params, fetchall=True)
    majors = query('SELECT major_id, major_name FROM Major ORDER BY major_id', fetchall=True)
    return render_template('major_change_list.html', changes=rows, majors=majors, search=search)

@major_bp.route('/change/create', methods=['POST'])
def change_create():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    sid = request.form.get('student_id', '')
    old_mid = request.form.get('old_major_id', '') or None
    new_mid = request.form.get('new_major_id', '')
    date = request.form.get('change_date', '')
    reason = request.form.get('reason', '')
    query('''INSERT INTO MajorChange (student_id,old_major_id,new_major_id,change_date,reason)
             VALUES (%s,%s,%s,%s,%s)''', (sid, old_mid, new_mid, date, reason))
    flash('专业变更记录已添加')
    return redirect(url_for('major.changes'))

@major_bp.route('/change/approve/<int:cid>')
def change_approve(cid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        with transaction() as cur:
            # 1. 更新变更记录状态
            cur.execute('UPDATE MajorChange SET status=%s WHERE change_id=%s', ('已通过', cid))
            # 2. 获取该变更记录中的学生和新专业
            cur.execute('SELECT student_id, new_major_id FROM MajorChange WHERE change_id=%s', (cid,))
            mc = cur.fetchone()
            if mc:
                # 3. 同步更新学生当前专业
                cur.execute('UPDATE Student SET major_id=%s WHERE student_id=%s', (mc[1], mc[0]))
        flash('变更已通过，学生专业已同步更新（事务已提交）')
    except Exception as e:
        flash(f'审批操作失败，事务已回滚: {e}')
    return redirect(url_for('major.changes'))

@major_bp.route('/change/reject/<int:cid>')
def change_reject(cid):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    query('UPDATE MajorChange SET status="已驳回" WHERE change_id=%s', (cid,))
    flash('变更已驳回')
    return redirect(url_for('major.changes'))

@major_bp.route('/change/stats')
def change_stats():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    stats = query('''SELECT m.major_name, m.department,
                     SUM(CASE WHEN mc.new_major_id=m.major_id AND mc.status="已通过" THEN 1 ELSE 0 END) AS transfer_in,
                     SUM(CASE WHEN mc.old_major_id=m.major_id AND mc.status="已通过" THEN 1 ELSE 0 END) AS transfer_out
                     FROM Major m
                     LEFT JOIN MajorChange mc ON (m.major_id=mc.new_major_id OR m.major_id=mc.old_major_id)
                     GROUP BY m.major_id, m.major_name, m.department
                     ORDER BY m.major_id''', fetchall=True)
    return render_template('major_change_stats.html', stats=stats)