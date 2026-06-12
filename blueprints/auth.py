from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database_helper import query

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'admin')  # 'admin' or 'student'

        if role == 'admin':
            # ========== 管理员登录 ==========
            row = query(
                'SELECT admin_id, username, password_hash FROM Admin WHERE username=%s',
                (username,), fetchone=True
            )
            if row and row[2] == password:
                session['admin_id'] = row[0]
                session['username'] = row[1]
                session['role'] = 'admin'
                flash('管理员登录成功')
                return redirect(url_for('student.list'))
            flash('管理员用户名或密码错误')
            return redirect(url_for('auth.login'))

        elif role == 'student':
            # ========== 学生登录 ==========
            row = query(
                'SELECT student_id, name, password_hash FROM Student WHERE student_id=%s AND is_deleted=0',
                (username,), fetchone=True
            )
            if row and row[2] == password:
                session['student_id'] = row[0]
                session['student_name'] = row[1]
                session['role'] = 'student'
                flash(f'欢迎回来，{row[1]}同学！')
                return redirect(url_for('portal.dashboard'))
            flash('学号或密码错误')
            return redirect(url_for('auth.login'))

        else:
            flash('无效的角色选择')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# ==================== 管理员专属路由 ====================

@auth_bp.route('/admin/list')
def admin_list():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    rows = query('SELECT admin_id, username, created_at FROM Admin ORDER BY admin_id', fetchall=True)
    return render_template('admin_list.html', admins=rows)


@auth_bp.route('/admin/create', methods=['POST'])
def admin_create():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    query('INSERT INTO Admin (username, password_hash) VALUES (%s, %s)', (username, password))
    flash('管理员创建成功')
    return redirect(url_for('auth.admin_list'))


@auth_bp.route('/admin/delete/<int:aid>')
def admin_delete(aid):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    query('DELETE FROM Admin WHERE admin_id=%s', (aid,))
    flash('管理员已删除')
    return redirect(url_for('auth.admin_list'))


# ==================== 通用：修改密码 ====================

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'admin_id' not in session and 'student_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        old_pw = request.form.get('old_password', '').strip()
        new_pw = request.form.get('new_password', '').strip()

        role = session.get('role')
        if role == 'admin':
            row = query('SELECT password_hash FROM Admin WHERE admin_id=%s',
                        (session['admin_id'],), fetchone=True)
            if row and row[0] == old_pw:
                query('UPDATE Admin SET password_hash=%s WHERE admin_id=%s',
                      (new_pw, session['admin_id']))
                flash('密码修改成功')
            else:
                flash('原密码错误')

        elif role == 'student':
            row = query('SELECT password_hash FROM Student WHERE student_id=%s',
                        (session['student_id'],), fetchone=True)
            if row and row[0] == old_pw:
                query('UPDATE Student SET password_hash=%s WHERE student_id=%s',
                      (new_pw, session['student_id']))
                flash('密码修改成功')
            else:
                flash('原密码错误')

        return redirect(url_for('auth.change_password'))

    return render_template('change_password.html')