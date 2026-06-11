# config.py - 应用配置
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MySQL 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'database': 'student_management',
    'charset': 'utf8mb4'
}

# Flask 配置
SECRET_KEY = 'student-management-secret-key-2026'

# 文件上传配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}