"""初始化数据库：执行 database/ 下所有SQL文件"""
import pymysql
import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'charset': 'utf8mb4'
}
MYSQL_CLI = ['mysql', '-u', 'root', '-pmysql123', '--default-character-set=utf8mb4', '--skip-show-database']


def run_with_cli(filepath, database='student_management'):
    """用MySQL CLI执行SQL文件(处理DELIMITER)"""
    import sys
    is_win = sys.platform == 'win32'
    
    # 使用 < 文件重定向，让MySQL CLI直接读取文件以保持编码
    if is_win:
        cmd_str = f'mysql -u root -pmysql123 --default-character-set=utf8mb4 {database} < "{filepath}"'
    else:
        cmd_str = f'mysql -u root -pmysql123 --default-character-set=utf8mb4 {database} < "{filepath}"'
    
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=False)
    
    if result.stderr:
        stderr = result.stderr.decode('gbk' if is_win else 'utf-8', errors='replace')
        errors = [l for l in stderr.split('\n') if 'Warning' not in l and 'warning' not in l.lower() and l.strip()]
        if errors:
            print(f'  [ERR] {errors[:3]}')


def run_simple_sql(cursor, filepath):
    """用pymysql执行简单SQL文件(不含复合语句)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    statements = [s.strip() for s in sql.split(';') 
                  if s.strip() and not s.strip().startswith('USE ') and not s.strip().startswith('DELIMITER')]
    for stmt in statements:
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f'  [WARN] {e}')


# 0. 创建数据库
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute('DROP DATABASE IF EXISTS student_management')
cur.execute('CREATE DATABASE student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
print('0. Database student_management created/recreated')
cur.close()
conn.close()

# 1. init.sql - 表结构 (简单SQL, pymysql可执行)
DB_CONFIG['database'] = 'student_management'
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
print('1. Running init.sql ...')
run_simple_sql(cur, os.path.join(BASE, 'database', 'init.sql'))
conn.commit()
print('   Tables created.')
cur.execute("SHOW TABLES")
tables = [t[0] for t in cur.fetchall()]
print(f'   Tables: {tables}')
cur.close()
conn.close()

# 2-4. 复合语句文件 (含DELIMITER, 用MySQL CLI执行)
for i, (name, fname) in enumerate([
    ('Functions', 'functions.sql'),
    ('Procedures', 'procedures.sql'),
    ('Triggers', 'triggers.sql'),
], 2):
    print(f'{i}. Running {fname} ...')
    run_with_cli(os.path.join(BASE, 'database', fname))
    print(f'   {name} executed.')

# 验证数据库对象
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='student_management'")
routines = cur.fetchall()
print(f'   Routines: {[(r[0], r[1]) for r in routines]}')

cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='student_management'")
triggers = [t[0] for t in cur.fetchall()]
print(f'   Triggers: {triggers}')
cur.close()
conn.close()

# 5. seed.sql - 种子数据 (必须在transactions之前,因为transactions依赖种子数据)
print('5. Running seed.sql ...')
run_with_cli(os.path.join(BASE, 'database', 'seed.sql'))
print('   Seed data inserted.')

# 6. transactions.sql (依赖种子数据,包含示例事务操作)
print('6. Running transactions.sql ...')
run_with_cli(os.path.join(BASE, 'database', 'transactions.sql'))
print('   Transactions executed.')

# 最终验证
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()
for tbl in ['Admin', 'Student', 'Major', 'Course', 'Enrollment', 'Score', 'RewardPunish', 'MajorChange']:
    try:
        cur.execute(f'SELECT COUNT(*) FROM `{tbl}`')
        cnt = cur.fetchone()[0]
        print(f'   {tbl}: {cnt} rows')
    except Exception as e:
        print(f'   {tbl}: error - {e}')
cur.close()
conn.close()
print('\n=== DATABASE INITIALIZATION COMPLETE ===')
