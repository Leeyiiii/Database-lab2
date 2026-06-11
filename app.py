
from flask import Flask, redirect, url_for
from config import SECRET_KEY, UPLOAD_FOLDER
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 注册蓝图
from blueprints.auth import auth_bp
from blueprints.student import student_bp
from blueprints.major import major_bp
from blueprints.reward_punish import rp_bp
from blueprints.course import course_bp
from blueprints.score import score_bp
from blueprints.enrollment import enrollment_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(major_bp, url_prefix='/major')
app.register_blueprint(rp_bp, url_prefix='/rp')
app.register_blueprint(course_bp, url_prefix='/course')
app.register_blueprint(score_bp, url_prefix='/score')
app.register_blueprint(enrollment_bp, url_prefix='/enrollment')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
